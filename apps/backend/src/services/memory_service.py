"""
memory_service.py — Serviço de leitura de memória do MHW.

Wrapper limpo sobre memory_reader, expondo apenas o necessário para as rotas.
"""

import sys
import os

# Garantir que o backend original está acessível
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
_old_backend = os.path.join(_root, "backend")
if _old_backend not in sys.path:
    sys.path.insert(0, _old_backend)

import memory_reader  # type: ignore


def get_reader():
    """Retorna a instância singleton do leitor de memória."""
    return memory_reader.get_reader()


def lookup_name(table: str, item_id: int) -> str:
    """Traduz um ID para nome usando o banco."""
    return memory_reader._lookup_name(table, item_id)


def lookup_monster_name(monster_id: int) -> str:
    """Traduz ID de monstro para nome."""
    return memory_reader._lookup_monster_name(monster_id)


def lookup_skill_name(skill_id: int) -> str:
    """Traduz ID de skill para nome."""
    return memory_reader._lookup_skill_name(skill_id)


PYMEM_AVAILABLE = memory_reader.PYMEM_AVAILABLE
