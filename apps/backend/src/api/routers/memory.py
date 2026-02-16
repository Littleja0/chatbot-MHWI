"""
memory.py — Router de leitura de memória do MHW (/memory/*).
"""

import os
from fastapi import APIRouter  # type: ignore
from fastapi.responses import FileResponse  # type: ignore

from services.memory_service import get_reader, lookup_name, lookup_monster_name, lookup_skill_name, PYMEM_AVAILABLE

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/status")
async def memory_status():
    reader = get_reader()
    return {
        "connected": reader.is_connected(),
        "pymem_available": PYMEM_AVAILABLE,
    }


@router.post("/connect")
async def memory_connect():
    reader = get_reader()
    success = reader.connect()
    return {"connected": success, "error": None if success else "MHW não encontrado. Abra o jogo primeiro."}


@router.post("/disconnect")
async def memory_disconnect():
    reader = get_reader()
    reader.disconnect()
    return {"connected": False}


@router.get("/snapshot")
async def memory_snapshot():
    reader = get_reader()
    return reader.get_full_snapshot()


@router.get("/fresh")
async def memory_fresh_snapshot():
    """Retorna snapshot FRESCO (sem cache)."""
    reader = get_reader()
    return reader.get_fresh_snapshot()


@router.get("/player")
async def memory_player():
    reader = get_reader()
    if not reader.is_connected():
        return {"connected": False}
    data = reader.get_player_info()
    data["connected"] = True
    return data


@router.get("/weapon")
async def memory_weapon():
    reader = get_reader()
    if not reader.is_connected():
        return {"connected": False}
    data = reader.get_weapon_info()
    wid = data.get("id")
    if wid and wid > 0:
        data["name"] = lookup_name("weapon", wid)
    data["connected"] = True
    return data


@router.get("/equipment")
async def memory_equipment():
    reader = get_reader()
    if not reader.is_connected():
        return {"connected": False}
    raw = reader.get_equipment_info()
    result = {"connected": True, "pieces": {}}
    slot_labels = {
        "head_id": "Elmo", "chest_id": "Torso", "arms_id": "Braços",
        "waist_id": "Cinturão", "legs_id": "Grevas", "charm_id": "Amuleto"
    }
    for key, label in slot_labels.items():
        eid = raw.get(key)
        if eid and eid > 0:
            table = "charm" if "charm" in key else "armor"
            result["pieces"][label] = {"id": eid, "name": lookup_name(table, eid)}
    return result


@router.get("/monsters")
async def memory_monsters():
    reader = get_reader()
    if not reader.is_connected():
        return {"connected": False, "monsters": []}
    monsters = reader.get_monsters()
    for m in monsters:
        m["name"] = lookup_monster_name(m["id"])
    return {"connected": True, "monsters": monsters}


@router.get("/skills")
async def memory_skills():
    reader = get_reader()
    if not reader.is_connected():
        return {"connected": False, "skills": []}
    skills = reader.get_active_skills()
    for s in skills:
        s["name"] = lookup_skill_name(s["id"])
    return {"connected": True, "skills": skills}


@router.get("/damage")
async def memory_damage():
    reader = get_reader()
    if not reader.is_connected():
        return {"connected": False, "players": [], "total_damage": 0}
    players = reader.get_party_damage()
    total = sum(p["damage"] for p in players) if players else 0
    return {"connected": True, "players": players, "total_damage": total}


@router.get("/abnormalities")
async def memory_abnormalities():
    reader = get_reader()
    if not reader.is_connected():
        return {"connected": False}
    data = reader.get_abnormalities()
    data["connected"] = True
    return data
