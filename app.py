"""Aplicação principal do Assistente Financeiro IA."""
import logging
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from config import Config
from models import User, Chat, Message
from services import ai_service, validation_service

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validação de configuração
Config.validate_config()

app = Flask(__name__)
app.config.from_object(Config)

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

@app.errorhandler(404)
def not_found_error(error):
    """Handler para erro 404."""
    return render_template('error.html', error="Página não encontrada"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para erro 500."""
    logger.error("Erro interno: %s", str(error))
    return render_template('error.html', error="Erro interno do servidor"), 500

@app.before_request
def security_headers():
    """Adiciona headers de segurança."""
    if request.endpoint and request.endpoint.startswith('static'):
        return
    
    # Headers de segurança básicos já são definidos no Config

def require_auth():
    """Decorator para rotas que requerem autenticação."""
    if "usuario" not in session:
        return redirect(url_for("login"))
    return None

@app.route("/")
def home():
    """Página principal."""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    try:
        chats = Chat.get_by_user(session["usuario"])
        return render_template("chat.html", usuario=session["usuario"], chats=chats)
    except Exception as e:
        logger.error("Erro ao carregar página principal: %s", str(e))
        flash("Erro ao carregar chats.")
        return render_template("chat.html", usuario=session["usuario"], chats=[])

@app.route("/registrar", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def registrar():
    """Registro de usuário."""
    if request.method == "POST":
        try:
            nome = request.form.get("nome", "").strip()
            senha = request.form.get("senha", "")
            
            # Validação
            is_valid, error_msg = validation_service.validate_user_input(nome, senha)
            if not is_valid:
                flash(error_msg)
                return render_template("registrar.html")
            
            # Criação do usuário
            if User.create(nome, senha):
                flash("Usuário criado com sucesso!")
                return redirect(url_for("login"))
            else:
                flash("Usuário já existe ou erro interno.")
                
        except Exception as e:
            logger.error("Erro no registro: %s", str(e))
            flash("Erro interno. Tente novamente.")
    
    return render_template("registrar.html")

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    """Login de usuário."""
    if request.method == "POST":
        try:
            nome = request.form.get("nome", "").strip()
            senha = request.form.get("senha", "")
            
            if not nome or not senha:
                flash("Nome e senha são obrigatórios.")
                return render_template("login.html")
            
            if User.authenticate(nome, senha):
                session["usuario"] = nome
                session.permanent = True
                return redirect(url_for("home"))
            else:
                flash("Usuário ou senha incorretos.")
                
        except Exception as e:
            logger.error("Erro no login: %s", str(e))
            flash("Erro interno. Tente novamente.")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Logout do usuário."""
    session.clear()
    return redirect(url_for("login"))

@app.route("/api/novo-chat", methods=["POST"])
@limiter.limit("10 per minute")
def novo_chat():
    """Cria um novo chat."""
    auth_check = require_auth()
    if auth_check:
        return jsonify({"erro": "Não autenticado"}), 401
    
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("JSON inválido")
        
        titulo = data.get("titulo", "Novo Chat").strip()
        
        # Validação
        is_valid, error_msg = validation_service.validate_chat_title(titulo)
        if not is_valid:
            return jsonify({"erro": error_msg}), 400
        
        chat_id = Chat.create(session["usuario"], titulo)
        if chat_id:
            return jsonify({"chat_id": chat_id, "titulo": titulo})
        else:
            return jsonify({"erro": "Erro ao criar chat"}), 500
            
    except BadRequest:
        return jsonify({"erro": "Dados inválidos"}), 400
    except Exception as e:
        logger.error("Erro ao criar chat: %s", str(e))
        return jsonify({"erro": "Erro interno"}), 500

@app.route("/api/chat/<int:chat_id>/mensagens")
@limiter.limit("30 per minute")
def obter_mensagens(chat_id):
    """Obtém mensagens de um chat."""
    auth_check = require_auth()
    if auth_check:
        return jsonify({"erro": "Não autenticado"}), 401
    
    try:
        mensagens = Message.get_by_chat(chat_id, session["usuario"])
        return jsonify({"mensagens": mensagens})
    except Exception as e:
        logger.error("Erro ao obter mensagens: %s", str(e))
        return jsonify({"erro": "Erro interno"}), 500

@app.route("/api/chat/<int:chat_id>", methods=["POST"])
@limiter.limit("20 per minute")
def enviar_mensagem(chat_id):
    """Envia mensagem para um chat."""
    auth_check = require_auth()
    if auth_check:
        return jsonify({"erro": "Não autenticado"}), 401
    
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("JSON inválido")
        
        pergunta = data.get("pergunta", "").strip()
        
        # Validação
        is_valid, error_msg = validation_service.validate_message(pergunta)
        if not is_valid:
            return jsonify({"erro": error_msg}), 400
        
        # Busca histórico
        historico_db = Message.get_history(chat_id, session["usuario"])
        historico = [{"role": m["role"], "content": m["conteudo"]} for m in historico_db]
        
        # Gera resposta da IA
        resposta_ia = ai_service.generate_response(pergunta, historico)
        
        # Salva mensagens
        Message.create(chat_id, session["usuario"], "user", pergunta)
        Message.create(chat_id, session["usuario"], "assistant", resposta_ia)
        
        return jsonify({"resposta": resposta_ia})
        
    except BadRequest:
        return jsonify({"erro": "Dados inválidos"}), 400
    except Exception as e:
        logger.error("Erro ao enviar mensagem: %s", str(e))
        return jsonify({"erro": "Erro interno"}), 500

@app.route("/api/chat/<int:chat_id>", methods=["DELETE"])
@limiter.limit("10 per minute")
def deletar_chat(chat_id):
    """Deleta um chat."""
    auth_check = require_auth()
    if auth_check:
        return jsonify({"erro": "Não autenticado"}), 401
    
    try:
        if Chat.delete(chat_id, session["usuario"]):
            return jsonify({"sucesso": True})
        else:
            return jsonify({"erro": "Chat não encontrado"}), 404
    except Exception as e:
        logger.error("Erro ao deletar chat: %s", str(e))
        return jsonify({"erro": "Erro interno"}), 500

if __name__ == "__main__":
    app.run(debug=False, host='127.0.0.1', port=5000)