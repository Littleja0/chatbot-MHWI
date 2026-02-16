
import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Tabela de Chats (Sessões)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            is_pinned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Tabela de Mensagens
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
        )
    """)
    # Tabela de Configuração do Usuário (Profile)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_config (
            id TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

def create_chat(title="Nova Conversa"):
    chat_id = str(uuid.uuid4())
    conn = get_db_connection()
    conn.execute("INSERT INTO chats (id, title) VALUES (?, ?)", (chat_id, title))
    conn.commit()
    conn.close()
    return chat_id

def get_all_chats():
    conn = get_db_connection()
    chats = conn.execute("SELECT * FROM chats ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(chat) for chat in chats]

def get_chat_messages(chat_id):
    conn = get_db_connection()
    messages = conn.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY timestamp ASC", (chat_id,)).fetchall()
    conn.close()
    return [dict(msg) for msg in messages]

def add_message(chat_id, role, content):
    msg_id = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp() * 1000)
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO messages (id, chat_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
        (msg_id, chat_id, role, content, timestamp)
    )
    # Atualizar timestamp do chat
    conn.execute("UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return msg_id

def delete_chat(chat_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()

def toggle_pin(chat_id):
    conn = get_db_connection()
    conn.execute("UPDATE chats SET is_pinned = 1 - is_pinned WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()

def update_chat_title(chat_id, title):
    conn = get_db_connection()
    conn.execute("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id))
    conn.commit()
    conn.close()

def set_user_config(config_id, value):
    conn = get_db_connection()
    if isinstance(value, (dict, list)):
        import json
        value = json.dumps(value)
    conn.execute("INSERT OR REPLACE INTO user_config (id, value) VALUES (?, ?)", (config_id, value))
    conn.commit()
    conn.close()

def get_user_config(config_id, default=None):
    conn = get_db_connection()
    row = conn.execute("SELECT value FROM user_config WHERE id = ?", (config_id,)).fetchone()
    conn.close()
    if row:
        val = row['value']
        try:
            import json
            return json.loads(val)
        except:
            return val
    return default

# Inicializar ao importar
init_db()
