"""Configurações da aplicação."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Classe de configuração da aplicação."""
    
    SECRET_KEY = os.getenv('SECRET_KEY')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'projeto_ia')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Configurações de segurança
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # Configurações de rate limiting
    RATELIMIT_STORAGE_URL = "memory://"
    
    @classmethod
    def validate_config(cls):
        """Valida se todas as configurações obrigatórias estão presentes."""
        required_vars = ['SECRET_KEY', 'GROQ_API_KEY']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Variáveis de ambiente obrigatórias não encontradas: {', '.join(missing_vars)}")