"""
equipment.py — Router de dados de equipamento para o Build Builder.

Endpoints:
  GET /equipment/weapons      — Lista armas com filtros
  GET /equipment/armor        — Lista armaduras com filtros
  GET /equipment/decorations  — Lista todas as joias
  GET /equipment/charms       — Lista todos os amuletos
  GET /equipment/set-bonuses  — Lista todos os set bonuses
"""

from typing import Optional
from fastapi import APIRouter, Query  # type: ignore
from core.mhw.mhw_api import get_db_connection

router = APIRouter(prefix="/equipment", tags=["equipment"])


# ============================================================
# Helpers
# ============================================================

def _get_text(conn, table: str, item_id: int, lang: str = 'pt') -> Optional[str]:
    """Get the name from a text table with pt->en fallback."""
    row = conn.execute(
        f"SELECT name FROM {table} WHERE id = ? AND lang_id = ?",
        (item_id, lang)
    ).fetchone()
    if row:
        return row['name']
    row = conn.execute(
        f"SELECT name FROM {table} WHERE id = ? AND lang_id = 'en'",
        (item_id,)
    ).fetchone()
    return row['name'] if row else None


# ============================================================
# GET /equipment/weapons
# ============================================================

@router.get("/weapons")
async def list_weapons(
    type: Optional[str] = Query(None, description="Weapon type filter (e.g. great-sword, long-sword)"),
    element: Optional[str] = Query(None, description="Element filter (e.g. fire, water, thunder, ice, dragon)"),
    rank: Optional[str] = Query(None, description="Rank filter: LR, HR, MR"),
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    conn = get_db_connection()
    try:
        # We'll fetch all weapons and join with text potentially in two languages
        params = []
        
        # Base query structure: prefer PT, fallback to EN names
        # We filter later in the results if search prompt is given
        
        conditions = []
        if type:
            conditions.append("w.weapon_type = ?")
            params.append(type)
        if element:
            conditions.append("LOWER(w.element1) = LOWER(?)")
            params.append(element)
        if rank:
            # HR/LR vs MR based on rarity
            rank_map = {'LR': (1, 4), 'HR': (5, 8), 'MR': (9, 12)}
            r = rank_map.get(rank.upper(), (1, 12))
            conditions.append("w.rarity BETWEEN ? AND ?")
            params.extend(r)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        query = f"""
            SELECT w.id, w.weapon_type, w.rarity, w.attack, w.attack_true,
                   w.affinity, w.defense, w.element1, w.element1_attack, w.element_hidden,
                   w.elderseal, w.slot_1, w.slot_2, w.slot_3, w.sharpness,
                   w.final, w.armorset_bonus_id, w.category
            FROM weapon w
            {where_clause}
            ORDER BY w.rarity DESC, w.attack DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        weapons = conn.execute(query, params).fetchall()

        results = []
        for w in weapons:
            # Get Names (PT and EN)
            pt_name = _get_text(conn, 'weapon_text', w['id'], 'pt')
            en_name = _get_text(conn, 'weapon_text', w['id'], 'en')
            
            name = pt_name or en_name
            
            # Manual Fix: Mapear Noite mais Escura se encontrarmos Deepest Night
            if en_name == "Deepest Night" and not pt_name:
                name = "Noite mais Escura"

            # Apply search filter client-side in results or here
            if search:
                s = search.lower()
                if s not in name.lower() and (not en_name or s not in en_name.lower()):
                    continue

            slots = [s for s in [w['slot_1'], w['slot_2'], w['slot_3']] if s and s > 0]

            results.append({
                "id": w['id'],
                "name": name,
                "name_en": en_name,
                "type": w['weapon_type'],
                "rarity": w['rarity'],
                "attack": w['attack'],
                "attack_true": w['attack_true'],
                "affinity": w['affinity'],
                "defense": w['defense'] or 0,
                "element": {"type": w['element1'], "damage": w['element1_attack'], "hidden": bool(w['element_hidden'])} if w['element1'] else None,
                "elderseal": w['elderseal'],
                "slots": slots,
                "is_final": bool(w['final']),
                "armorset_bonus_id": w['armorset_bonus_id'],
                "category": w['category'],
            })

        return {"items": results, "total": len(results), "offset": offset}
    except Exception as e:
        return {"error": str(e), "items": []}
    finally:
        conn.close()


# ============================================================
# GET /equipment/armor
# ============================================================

@router.get("/armor")
async def list_armor(
    type: Optional[str] = Query(None, description="Armor type: head, chest, arms, waist, legs"),
    rank: Optional[str] = Query(None, description="Rank filter: LR, HR, MR"),
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    conn = get_db_connection()
    try:
        conditions = ["at.lang_id = 'pt'"]
        params = []

        if type:
            conditions.append("a.armor_type = ?")
            params.append(type)
        if rank:
            conditions.append("a.rank = ?")
            params.append(rank.upper())
        if search:
            conditions.append("at.name LIKE ?")
            params.append(f"%{search}%")

        where = " AND ".join(conditions)

        query = f"""
            SELECT a.id, at.name, a.armor_type, a.rank, a.rarity,
                   a.defense_base, a.defense_max, a.defense_augment_max,
                   a.fire, a.water, a.thunder, a.ice, a.dragon,
                   a.slot_1, a.slot_2, a.slot_3,
                   a.armorset_id
            FROM armor a
            JOIN armor_text at ON a.id = at.id
            WHERE {where}
            ORDER BY a.rarity DESC, a.defense_base DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        armors = conn.execute(query, params).fetchall()

        results = []
        for a in armors:
            # Skills
            skills = conn.execute("""
                SELECT st.name, ars.level
                FROM armor_skill ars
                JOIN skilltree_text st ON ars.skilltree_id = st.id
                WHERE ars.armor_id = ? AND st.lang_id = 'pt'
            """, (a['id'],)).fetchall()

            if not skills:
                skills = conn.execute("""
                    SELECT st.name, ars.level
                    FROM armor_skill ars
                    JOIN skilltree_text st ON ars.skilltree_id = st.id
                    WHERE ars.armor_id = ? AND st.lang_id = 'en'
                """, (a['id'],)).fetchall()

            # Set name
            set_name = None
            if a['armorset_id']:
                set_name = _get_text(conn, 'armorset_text', a['armorset_id'])

            slots = [s for s in [a['slot_1'], a['slot_2'], a['slot_3']] if s and s > 0]

            results.append({
                "id": a['id'],
                "name": a['name'],
                "type": a['armor_type'],
                "rank": a['rank'],
                "rarity": a['rarity'],
                "set_name": set_name,
                "defense": {"base": a['defense_base'], "max": a['defense_max']},
                "resistances": {
                    "fire": a['fire'], "water": a['water'], "thunder": a['thunder'],
                    "ice": a['ice'], "dragon": a['dragon']
                },
                "slots": slots,
                "skills": [{"name": s['name'], "level": s['level']} for s in skills],
            })

        return {"items": results, "total": len(results), "offset": offset}
    except Exception as e:
        return {"error": str(e), "items": []}
    finally:
        conn.close()


# ============================================================
# GET /equipment/decorations
# ============================================================

@router.get("/decorations")
async def list_decorations(
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(500, ge=1, le=1000),
):
    conn = get_db_connection()
    try:
        conditions = ["dt.lang_id = 'pt'"]
        params = []

        if search:
            conditions.append("dt.name LIKE ?")
            params.append(f"%{search}%")

        where = " AND ".join(conditions)

        query = f"""
            SELECT d.id, dt.name, d.slot, d.rarity,
                   d.skilltree_id, d.skilltree_level,
                   d.skilltree2_id, d.skilltree2_level
            FROM decoration d
            JOIN decoration_text dt ON d.id = dt.id
            WHERE {where}
            ORDER BY d.slot DESC, dt.name
            LIMIT ?
        """
        params.append(limit)
        decos = conn.execute(query, params).fetchall()

        results = []
        for d in decos:
            skills = []

            # Primary skill
            skill_name = _get_text(conn, 'skilltree_text', d['skilltree_id'])
            if skill_name:
                skills.append({"name": skill_name, "level": d['skilltree_level']})

            # Secondary skill (rare, e.g. Expert+ Jewel 4)
            if d['skilltree2_id']:
                skill2_name = _get_text(conn, 'skilltree_text', d['skilltree2_id'])
                if skill2_name:
                    skills.append({"name": skill2_name, "level": d['skilltree2_level']})

            results.append({
                "id": d['id'],
                "name": d['name'],
                "tier": d['slot'],
                "rarity": d['rarity'],
                "skills": skills,
            })

        return {"items": results, "total": len(results)}
    except Exception as e:
        return {"error": str(e), "items": []}
    finally:
        conn.close()


# ============================================================
# GET /equipment/charms
# ============================================================

@router.get("/charms")
async def list_charms(
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(500, ge=1, le=1000),
):
    conn = get_db_connection()
    try:
        conditions = ["ct.lang_id = 'pt'"]
        params = []

        if search:
            conditions.append("ct.name LIKE ?")
            params.append(f"%{search}%")

        where = " AND ".join(conditions)

        query = f"""
            SELECT c.id, ct.name, c.rarity
            FROM charm c
            JOIN charm_text ct ON c.id = ct.id
            WHERE {where}
            ORDER BY c.rarity DESC, ct.name
            LIMIT ?
        """
        params.append(limit)
        charms = conn.execute(query, params).fetchall()

        results = []
        for ch in charms:
            skills = conn.execute("""
                SELECT st.name, cs.level
                FROM charm_skill cs
                JOIN skilltree_text st ON cs.skilltree_id = st.id
                WHERE cs.charm_id = ? AND st.lang_id = 'pt'
            """, (ch['id'],)).fetchall()

            if not skills:
                skills = conn.execute("""
                    SELECT st.name, cs.level
                    FROM charm_skill cs
                    JOIN skilltree_text st ON cs.skilltree_id = st.id
                    WHERE cs.charm_id = ? AND st.lang_id = 'en'
                """, (ch['id'],)).fetchall()

            results.append({
                "id": ch['id'],
                "name": ch['name'],
                "rarity": ch['rarity'],
                "skills": [{"name": s['name'], "level": s['level']} for s in skills],
            })

        return {"items": results, "total": len(results)}
    except Exception as e:
        return {"error": str(e), "items": []}
    finally:
        conn.close()


# ============================================================
# GET /equipment/set-bonuses
# ============================================================

@router.get("/set-bonuses")
async def list_set_bonuses():
    conn = get_db_connection()
    try:
        bonuses = conn.execute("""
            SELECT abt.id, abt.name
            FROM armorset_bonus_text abt
            WHERE abt.lang_id = 'pt'
            ORDER BY abt.name
        """).fetchall()

        # Fallback to English if no PT names
        if not bonuses:
            bonuses = conn.execute("""
                SELECT abt.id, abt.name
                FROM armorset_bonus_text abt
                WHERE abt.lang_id = 'en'
                ORDER BY abt.name
            """).fetchall()

        results = []
        for b in bonuses:
            # Get the skill tiers for this bonus
            tiers = conn.execute("""
                SELECT abs.required, st.name AS skill_name, st.description
                FROM armorset_bonus_skill abs
                JOIN skilltree_text st ON abs.skilltree_id = st.id
                WHERE abs.setbonus_id = ? AND st.lang_id = 'pt'
                ORDER BY abs.required
            """, (b['id'],)).fetchall()

            if not tiers:
                tiers = conn.execute("""
                    SELECT abs.required, st.name AS skill_name, st.description
                    FROM armorset_bonus_skill abs
                    JOIN skilltree_text st ON abs.skilltree_id = st.id
                    WHERE abs.setbonus_id = ? AND st.lang_id = 'en'
                    ORDER BY abs.required
                """, (b['id'],)).fetchall()

            results.append({
                "id": b['id'],
                "set_name": b['name'],
                "pieces": [
                    {
                        "required": t['required'],
                        "bonus_name": t['skill_name'],
                        "description": t['description'] or "",
                    }
                    for t in tiers
                ],
            })

        return {"items": results, "total": len(results)}
    except Exception as e:
        return {"error": str(e), "items": []}
    finally:
        conn.close()
