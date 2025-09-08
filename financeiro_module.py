# Módulo de funcionalidades financeiras removidas do app principal
# Para reintegrar depois: copie as funções necessárias de volta ao app.py

import os
import re
import fitz
from werkzeug.utils import secure_filename
from flask import request, flash, redirect, url_for, render_template, session

# Configurações
UPLOAD_FOLDER = 'uploads'

# Rotas financeiras
def upload_route(app, db):
    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        if "usuario" not in session:
            return redirect(url_for("login"))

        if request.method == "POST":
            arquivo = request.files.get("arquivo")
            if not arquivo or not arquivo.filename.endswith(".pdf"):
                flash("Envie um arquivo PDF válido.")
                return redirect(url_for("upload"))

            caminho = os.path.join(UPLOAD_FOLDER, secure_filename(arquivo.filename))
            arquivo.save(caminho)
            texto = extrair_texto_pdf(caminho)
            gastos = classificar_gastos(texto)

            gastos_ajustados = []
            for item in gastos:
                descricao = item.get('historico', '').strip()
                data = item.get('data', '').strip()
                valor = item.get('debito', 0.0)
                if valor == 0.0:
                    valor = item.get('credito', 0.0)
                if valor == 0.0:
                    continue

                categoria = categorizar(descricao)
                gastos_ajustados.append({
                    'data': data,
                    'descricao': descricao,
                    'valor': valor,
                    'categoria': categoria
                })

            salvar_gastos(session["usuario"], gastos_ajustados, db)
            flash("Extrato processado com sucesso!")
            return redirect(url_for("relatorio"))

        return render_template("upload.html", usuario=session["usuario"])

def relatorio_route(app, db):
    @app.route("/relatorio")
    def relatorio():
        if "usuario" not in session:
            return redirect(url_for("login"))

        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT data, descricao, categoria, valor FROM gastos
            WHERE usuario = %s
            ORDER BY data DESC
        """, (session["usuario"],))
        dados = cursor.fetchall()
        cursor.close()
        return render_template("relatorio.html", usuario=session["usuario"], dados=dados)

# Funções de processamento
def extrair_texto_pdf(caminho):
    doc = fitz.open(caminho)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    doc.close()
    return texto

def classificar_gastos(texto):
    linhas = [linha.strip() for linha in texto.split("\n") if linha.strip()]
    transacoes = []
    i = 0

    while i < len(linhas):
        if re.match(r"\d{2}/\d{2}/\d{4}", linhas[i]):
            data = linhas[i]
            i += 1

            historico_linhas = []
            while i < len(linhas) and not re.match(r"^\d{2}/\d{2}/\d{4}$", linhas[i]) and not re.match(r"^\d{1,3}\.\d{3},\d{2}$", linhas[i]):
                historico_linhas.append(linhas[i])
                i += 1
            historico = " ".join(historico_linhas)

            if i + 1 < len(linhas):
                valor_str = linhas[i].replace(".", "").replace(",", ".")
                saldo_str = linhas[i + 1].replace(".", "").replace(",", ".")
                i += 2
            else:
                valor_str = "0"
                saldo_str = "0"

            valor = try_float(valor_str)
            saldo = try_float(saldo_str)

            historico_lower = historico.lower()
            if "rem:" in historico_lower or "rendimento" in historico_lower or "depósito" in historico_lower:
                credito = valor
                debito = 0.0
            else:
                credito = 0.0
                debito = valor

            transacoes.append({
                "data": data,
                "historico": historico,
                "documento": "",
                "credito": credito,
                "debito": debito,
                "saldo": saldo
            })
        else:
            i += 1

    return transacoes

def try_float(valor_str):
    valor_str = valor_str.replace(".", "").replace(",", ".").strip()
    try:
        return float(valor_str)
    except ValueError:
        return 0.0

def categorizar(descricao):
    descricao = descricao.lower()
    if "uber" in descricao or "99" in descricao:
        return "Transporte"
    if "drogaria" in descricao or "raia" in descricao:
        return "Farmácia"
    if "mercado" in descricao or "horti" in descricao:
        return "Mercado"
    if "boteco" in descricao or "lanche" in descricao or "pipo" in descricao:
        return "Alimentação"
    if "claro" in descricao or "light" in descricao:
        return "Contas"
    return "Outros"

def salvar_gastos(usuario, lista, db):
    cursor = db.cursor()
    for item in lista:
        cursor.execute("""
            INSERT INTO gastos (usuario, data, descricao, valor, categoria)
            VALUES (%s, STR_TO_DATE(%s, '%d/%m/%Y'), %s, %s, %s)
        """, (usuario, item['data'], item['descricao'], item['valor'], item['categoria']))
    db.commit()
    cursor.close()