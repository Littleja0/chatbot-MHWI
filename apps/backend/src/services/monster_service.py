"""
monster_service.py — Serviço de dados de monstros.

Wrapper limpo sobre mhw_api e mhw_rag, expondo apenas o necessário.
"""

import sys
import os

# Garantir que o backend original está acessível (para mhw_api/mhw_rag originais)
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
_old_backend = os.path.join(_root, "backend")
if _old_backend not in sys.path:
    sys.path.insert(0, _old_backend)
if _root not in sys.path:
    sys.path.insert(0, _root)

# Import dos módulos originais (que ficam em backend/)
import mhw_api  # type: ignore
import mhw_rag  # type: ignore


def get_all_monster_names() -> list[str]:
    """Retorna lista de todos os nomes de monstros."""
    return mhw_rag.get_all_monster_names_from_xml()


def get_all_skill_caps() -> dict:
    """Retorna dict de skill_name -> max_level."""
    return mhw_api.get_all_skill_max_levels()


def get_monster_data(name: str) -> dict | None:
    """Busca dados de um monstro pelo nome."""
    data_list = mhw_api.get_monster_data(name)
    if not data_list:
        return None
    
    m = data_list[0]
    image_url = mhw_api.get_monster_image_url(m['name'])
    
    return {
        "name": m['name'],
        "species": m['species'],
        "description": m['description'],
        "weakness": m['weaknesses'],
        "resistances": m.get('resistances', []),
        "breakableParts": m.get('breaks', []),
        "rewards": m['rewards'],
        "image": image_url or f"https://picsum.photos/seed/{m['name']}/800/600"
    }


async def get_rag_context(prompt: str, history=None) -> str:
    """Proxy assíncrono para o RAG context."""
    return await mhw_rag.get_rag_context(prompt, history=history)
