"""
logging.py — Configuração centralizada de logging.
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configura e retorna o logger principal."""
    logger = logging.getLogger("mhw_chatbot")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Logger global
log = setup_logging()
