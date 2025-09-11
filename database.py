"""Módulo de gerenciamento de banco de dados."""
import logging
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerenciador de conexões com o banco de dados."""
    
    def __init__(self):
        self.config = {
            'host': Config.DB_HOST,
            'port': getattr(Config, 'DB_PORT', 3306),
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'autocommit': False,
            'charset': 'utf8mb4',
            'use_unicode': True,
            'pool_name': 'mypool',
            'pool_size': 5,
            'pool_reset_session': True
        }
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões com o banco."""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Error as e:
            logger.error("Erro na conexão com o banco: %s", str(e))
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @contextmanager
    def get_cursor(self, dictionary=False):
        """Context manager para cursors."""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary, buffered=True)
            try:
                yield cursor, connection
            except Error as e:
                logger.error("Erro na execução da query: %s", str(e))
                connection.rollback()
                raise
            else:
                connection.commit()
            finally:
                cursor.close()

db_manager = DatabaseManager()