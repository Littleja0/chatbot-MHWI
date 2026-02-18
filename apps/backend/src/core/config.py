"""
config.py — Configuração centralizada do backend.

Carrega variáveis de ambiente e define constantes do projeto.
"""

import sys
import os
import io
from pathlib import Path
from dotenv import load_dotenv  # type: ignore

# --- Platform Fixes ---
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
        sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')
    except (AttributeError, io.UnsupportedOperation):
        pass

# --- Paths ---
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))))
    ROOT_DIR = BASE_DIR
else:
    # Este arquivo: apps/backend/src/core/config.py
    # BASE_DIR será: apps/backend
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    ROOT_DIR = BASE_DIR.parent.parent

# --- Directories ---
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = ROOT_DIR / "data"
RAG_DIR = DATA_DIR / "rag"
STORAGE_DIR = DATA_DIR / "storage"
KNOWLEDGE_DIR = DATA_DIR / "knowledge_base"

# --- Environment ---
load_dotenv(ROOT_DIR / ".env")

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "").replace("Bearer ", "").strip()
os.environ["NVIDIA_API_KEY"] = NVIDIA_API_KEY

# --- Server ---
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# --- LLM ---
LLM_BASE_URL = "https://integrate.api.nvidia.com/v1"
LLM_MODEL = "moonshotai/kimi-k2-instruct-0905"
LLM_TIMEOUT = 60.0
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 2048

# --- DB Paths ---
MHW_DB_PATH = str(DATA_DIR / "mhw.db")
SESSIONS_DB_PATH = str(DATA_DIR / "sessions.db")

# Logic to enforce SSoT: files must exist in ROOT_DIR / data
if not os.path.exists(MHW_DB_PATH):
    print(f"CRITICAL ERROR: {MHW_DB_PATH} not found.")

# --- Constants ---
GREETINGS = ["olá", "oi", "bom dia", "boa tarde", "boa noite", "e aí", "opa", "hello", "hi", "eae"]

# Add paths for imports
for p in [str(BASE_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)
