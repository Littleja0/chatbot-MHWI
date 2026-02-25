import sqlite3
import os
import time
import logging

# Configuração de Logging para Performance
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path=None):
        if self._initialized:
            return
        
        if db_path is None:
            # Caminho padrão relativo à raiz do projeto
            self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'mhw.db')
        else:
            self.db_path = db_path

        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._initialized = True
        logger.info(f"Conexão estabelecida com {self.db_path}")

    def execute_query(self, query, params=()):
        start_time = time.perf_counter()
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            duration = (time.perf_counter() - start_time) * 1000
            if duration > 5:
                logger.warning(f"Query lenta detectada: {duration:.2f}ms - {query}")
            else:
                logger.debug(f"Query executada em {duration:.2f}ms")
            return result
        except sqlite3.Error as e:
            logger.error(f"Erro ao executar query: {e}")
            return []

    def get_decorations_by_skill(self, skill_name, lang='en', max_slot=4):
        """
        Busca joias que forneçam uma skill específica, filtrando pelo nível do slot.
        Retorna ordenado por raridade (mais raras primeiro).
        """
        query = """
            SELECT d.*, dt.name as decoration_name, st.name as skill_name
            FROM decoration d
            JOIN decoration_text dt ON d.id = dt.id AND dt.lang_id = ?
            JOIN skilltree_text st ON d.skilltree_id = st.id AND st.lang_id = ?
            WHERE st.name = ? AND d.slot <= ?
            UNION
            SELECT d.*, dt.name as decoration_name, st.name as skill_name
            FROM decoration d
            JOIN decoration_text dt ON d.id = dt.id AND dt.lang_id = ?
            JOIN skilltree_text st ON d.skilltree2_id = st.id AND st.lang_id = ?
            WHERE st.name = ? AND d.slot <= ?
            ORDER BY d.rarity DESC
        """
        params = (lang, lang, skill_name, max_slot, lang, lang, skill_name, max_slot)
        return self.execute_query(query, params)

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Conexão com o banco de dados encerrada.")

if __name__ == "__main__":
    # Teste rápido
    db = DatabaseManager()
    res = db.get_decorations_by_skill("Attack Boost")
    for row in res:
        print(f"Joia: {row['decoration_name']} | Slot: {row['slot']} | Rarity: {row['rarity']}")
    db.close()
