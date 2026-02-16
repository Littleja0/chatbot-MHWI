"""
monsters.py — Router de dados de monstros (/monster/*) e overlay.
"""

import os
from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import FileResponse  # type: ignore

from services.monster_service import get_monster_data
from core.config import TEMPLATES_DIR

router = APIRouter(tags=["monsters"])


@router.get("/monster/{name}")
async def get_monster(name: str):
    try:
        data = get_monster_data(name)
        if not data:
            raise HTTPException(status_code=404, detail="Monstro não encontrado no banco de dados.")
        return data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro API Monster: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/overlay/damage")
async def overlay_damage_page():
    overlay_path = TEMPLATES_DIR / "overlay_damage.html"
    # Fallback para localização antiga
    if not overlay_path.exists():
        old_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "backend", "overlay_damage.html")
        if os.path.exists(old_path):
            return FileResponse(old_path, media_type="text/html")
    return FileResponse(str(overlay_path), media_type="text/html")
