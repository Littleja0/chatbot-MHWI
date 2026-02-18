"""
monster_service.py — Serviço de dados de monstros.

Wrapper limpo sobre mhw_api e mhw_rag, expondo apenas o necessário.
"""

from core.mhw import mhw_api
from core.mhw import mhw_rag


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
