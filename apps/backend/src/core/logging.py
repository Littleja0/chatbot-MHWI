"""
logging.py — Configuração centralizada de logging.

No modo frozen (PyInstaller), grava logs em arquivo ao lado do .exe
para possibilitar diagnóstico sem console.
"""

import logging
import sys
import os
from pathlib import Path


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configura e retorna o logger principal."""
    logger = logging.getLogger("mhw_chatbot")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )

        # Console handler (funciona quando console está disponível)
        try:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        except Exception:
            pass

        # File handler — grava ao lado do executável (essencial para builds sem console)
        if getattr(sys, 'frozen', False):
            log_dir = Path(os.path.dirname(sys.executable))
        else:
            log_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        
        try:
            log_file = log_dir / "mhw_chatbot.log"
            file_handler = logging.FileHandler(str(log_file), encoding='utf-8', mode='w')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            pass

    return logger


# Logger global
log = setup_logging()
