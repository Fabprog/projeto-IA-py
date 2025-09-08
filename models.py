"""Modelos de dados da aplicação."""
import logging
import bcrypt
from datetime import datetime
from typing import List, Dict, Optional
from database import db_manager

logger = logging.getLogger(__name__)

class User:
    """Modelo de usuário."""
    
    @staticmethod
    def create(nome: str, senha: str) -> bool:
        """Cria um novo usuário."""
        try:
            if User.exists(nome):
                return False
            
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
            
            with db_manager.get_cursor() as (cursor, _):
                cursor.execute(
                    "INSERT INTO usuarios (nome, HASH) VALUES (%s, %s)",
                    (nome, senha_hash)
                )
            return True
        except Exception as e:
            logger.error("Erro ao criar usuário: %s", str(e))
            return False
    
    @staticmethod
    def authenticate(nome: str, senha: str) -> bool:
        """Autentica um usuário."""
        try:
            with db_manager.get_cursor() as (cursor, _):
                cursor.execute("SELECT HASH FROM usuarios WHERE nome = %s", (nome,))
                result = cursor.fetchone()
                
                if not result:
                    return False
                
                senha_hash = result[0]
                if isinstance(senha_hash, str):
                    senha_hash = senha_hash.encode('utf-8')
                
                return bcrypt.checkpw(senha.encode('utf-8'), senha_hash)
        except Exception as e:
            logger.error("Erro na autenticação: %s", str(e))
            return False
    
    @staticmethod
    def exists(nome: str) -> bool:
        """Verifica se um usuário existe."""
        try:
            with db_manager.get_cursor() as (cursor, _):
                cursor.execute("SELECT 1 FROM usuarios WHERE nome = %s", (nome,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error("Erro ao verificar usuário: %s", str(e))
            return False

class Chat:
    """Modelo de chat."""
    
    @staticmethod
    def create(usuario: str, titulo: str) -> Optional[int]:
        """Cria um novo chat."""
        try:
            with db_manager.get_cursor() as (cursor, _):
                cursor.execute(
                    "INSERT INTO chats (usuario, titulo) VALUES (%s, %s)",
                    (usuario, titulo)
                )
                return cursor.lastrowid
        except Exception as e:
            logger.error("Erro ao criar chat: %s", str(e))
            return None
    
    @staticmethod
    def get_by_user(usuario: str) -> List[Dict]:
        """Obtém todos os chats de um usuário."""
        try:
            with db_manager.get_cursor(dictionary=True) as (cursor, _):
                cursor.execute(
                    "SELECT id, titulo, criado_em FROM chats WHERE usuario = %s ORDER BY criado_em DESC",
                    (usuario,)
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error("Erro ao buscar chats: %s", str(e))
            return []
    
    @staticmethod
    def delete(chat_id: int, usuario: str) -> bool:
        """Deleta um chat e suas mensagens."""
        try:
            with db_manager.get_cursor() as (cursor, _):
                cursor.execute("DELETE FROM mensagens WHERE chat_id = %s AND usuario = %s", (chat_id, usuario))
                cursor.execute("DELETE FROM chats WHERE id = %s AND usuario = %s", (chat_id, usuario))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error("Erro ao deletar chat: %s", str(e))
            return False

class Message:
    """Modelo de mensagem."""
    
    @staticmethod
    def create(chat_id: int, usuario: str, role: str, conteudo: str) -> bool:
        """Cria uma nova mensagem."""
        try:
            with db_manager.get_cursor() as (cursor, _):
                cursor.execute(
                    "INSERT INTO mensagens (chat_id, usuario, role, conteudo) VALUES (%s, %s, %s, %s)",
                    (chat_id, usuario, role, conteudo)
                )
            return True
        except Exception as e:
            logger.error("Erro ao criar mensagem: %s", str(e))
            return False
    
    @staticmethod
    def get_by_chat(chat_id: int, usuario: str, limit: int = 50) -> List[Dict]:
        """Obtém mensagens de um chat."""
        try:
            with db_manager.get_cursor(dictionary=True) as (cursor, _):
                cursor.execute(
                    "SELECT role, conteudo, criado_em FROM mensagens WHERE chat_id = %s AND usuario = %s ORDER BY criado_em ASC LIMIT %s",
                    (chat_id, usuario, limit)
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error("Erro ao buscar mensagens: %s", str(e))
            return []
    
    @staticmethod
    def get_history(chat_id: int, usuario: str, limit: int = 10) -> List[Dict]:
        """Obtém histórico recente para contexto da IA."""
        try:
            with db_manager.get_cursor(dictionary=True) as (cursor, _):
                cursor.execute(
                    "SELECT role, conteudo FROM mensagens WHERE chat_id = %s AND usuario = %s ORDER BY criado_em DESC LIMIT %s",
                    (chat_id, usuario, limit)
                )
                return list(reversed(cursor.fetchall()))
        except Exception as e:
            logger.error("Erro ao buscar histórico: %s", str(e))
            return []