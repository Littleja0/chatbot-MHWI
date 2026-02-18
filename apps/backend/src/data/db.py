"""
db.py — Gerenciamento centralizado de conexões de banco de dados.

Fornece conexões para os dois bancos:
- sessions.db: Chats, mensagens e configurações do usuário.
- mhw.db: Dados extraídos do jogo (monstros, armaduras, etc.)
"""

import sqlite3
import os
import uuid
import json
from datetime import datetime
from typing import Any, Optional

from core.config import SESSIONS_DB_PATH, MHW_DB_PATH

def get_sessions_db() -> sqlite3.Connection:
    """Retorna conexão ao banco de sessões."""
    conn = sqlite3.connect(SESSIONS_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def get_mhw_db() -> sqlite3.Connection:
    """Retorna conexão ao banco de dados do jogo."""
    conn = sqlite3.connect(MHW_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_sessions_db():
    """Inicializa tabelas do banco de sessões."""
    conn = get_sessions_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            is_pinned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_config (
            id TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Chat Operations ---

def create_chat(title: str = "Nova Conversa") -> str:
    chat_id = str(uuid.uuid4())
    conn = get_sessions_db()
    conn.execute("INSERT INTO chats (id, title) VALUES (?, ?)", (chat_id, title))
    conn.commit()
    conn.close()
    return chat_id

def get_all_chats() -> list[dict]:
    conn = get_sessions_db()
    chats = conn.execute("SELECT * FROM chats ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(chat) for chat in chats]

def get_chat_messages(chat_id: str) -> list[dict]:
    conn = get_sessions_db()
    messages = conn.execute(
        "SELECT * FROM messages WHERE chat_id = ? ORDER BY timestamp ASC", (chat_id,)
    ).fetchall()
    conn.close()
    return [dict(msg) for msg in messages]

def add_message(chat_id: str, role: str, content: str) -> str:
    msg_id = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp() * 1000)
    conn = get_sessions_db()
    conn.execute(
        "INSERT INTO messages (id, chat_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
        (msg_id, chat_id, role, content, timestamp)
    )
    conn.execute("UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return msg_id

def delete_chat(chat_id: str):
    conn = get_sessions_db()
    conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()

def toggle_pin(chat_id: str):
    conn = get_sessions_db()
    conn.execute("UPDATE chats SET is_pinned = 1 - is_pinned WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()

def update_chat_title(chat_id: str, title: str):
    conn = get_sessions_db()
    conn.execute("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id))
    conn.commit()
    conn.close()

# --- User Config ---

def set_user_config(config_id: str, value: Any):
    conn = get_sessions_db()
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    conn.execute("INSERT OR REPLACE INTO user_config (id, value) VALUES (?, ?)", (config_id, value))
    conn.commit()
    conn.close()

def get_user_config(config_id: str, default: Any = None) -> Any:
    conn = get_sessions_db()
    row = conn.execute("SELECT value FROM user_config WHERE id = ?", (config_id,)).fetchone()
    conn.close()
    if row:
        val = row['value']
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return val
    return default

# Inicializar ao importar
init_sessions_db()
