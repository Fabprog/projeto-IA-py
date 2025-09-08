"""Serviços da aplicação."""
import logging
import requests
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class AIService:
    """Serviço de integração com IA."""
    
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "gemma2-9b-it"
        self.timeout = 30
        self.max_tokens = 1000
        self.temperature = 0.7
        
        self.system_prompt = (
            "Você é um assistente financeiro pessoal especializado. "
            "Suas principais funções são: "
            "1) Dar conselhos sobre investimentos, poupança e planejamento financeiro "
            "2) Explicar conceitos financeiros de forma simples "
            "3) Sugerir estratégias para economizar dinheiro "
            "4) Orientar sobre controle de gastos e orçamento pessoal "
            "5) Dar dicas sobre educação financeira "
            "6) Responder dúvidas sobre bancos, cartões e produtos financeiros. "
            "Sempre seja prático, didático e focado em soluções financeiras reais para o usuário brasileiro."
        )
    
    def generate_response(self, pergunta: str, historico: Optional[List[Dict]] = None) -> str:
        """Gera resposta da IA."""
        if not self.api_key:
            logger.error("GROQ_API_KEY não configurada")
            return "Erro: Serviço de IA não configurado."
        
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if historico:
                # Limita histórico para evitar payload muito grande
                messages.extend(historico[-5:])
            
            messages.append({"role": "user", "content": pergunta})
            
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error("Erro na API Groq: %s - %s", response.status_code, response.text)
                return "Erro na API. Tente novamente."
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except requests.exceptions.Timeout:
            logger.error("Timeout na API Groq")
            return "Erro: Tempo limite excedido. Tente novamente."
        except requests.exceptions.RequestException as e:
            logger.error("Erro na requisição para API Groq: %s", str(e))
            return "Erro: Não foi possível conectar à IA."
        except (KeyError, IndexError) as e:
            logger.error("Erro ao processar resposta da API: %s", str(e))
            return "Erro: Resposta inválida da IA."
        except Exception as e:
            logger.error("Erro inesperado no serviço de IA: %s", str(e))
            return "Erro: Falha no serviço de IA."

class ValidationService:
    """Serviço de validação de dados."""
    
    @staticmethod
    def validate_user_input(nome: str, senha: str) -> tuple[bool, str]:
        """Valida entrada de usuário."""
        if not nome or not senha:
            return False, "Nome e senha são obrigatórios."
        
        if len(nome) < 3 or len(nome) > 50:
            return False, "Nome deve ter entre 3 e 50 caracteres."
        
        if len(senha) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres."
        
        # Validação básica de caracteres
        if not nome.replace('_', '').replace('-', '').isalnum():
            return False, "Nome deve conter apenas letras, números, _ e -."
        
        return True, ""
    
    @staticmethod
    def validate_chat_title(titulo: str) -> tuple[bool, str]:
        """Valida título do chat."""
        if not titulo:
            return False, "Título é obrigatório."
        
        if len(titulo) > 255:
            return False, "Título muito longo (máximo 255 caracteres)."
        
        return True, ""
    
    @staticmethod
    def validate_message(conteudo: str) -> tuple[bool, str]:
        """Valida conteúdo da mensagem."""
        if not conteudo or not conteudo.strip():
            return False, "Mensagem não pode estar vazia."
        
        if len(conteudo) > 5000:
            return False, "Mensagem muito longa (máximo 5000 caracteres)."
        
        return True, ""

# Instâncias dos serviços
ai_service = AIService()
validation_service = ValidationService()