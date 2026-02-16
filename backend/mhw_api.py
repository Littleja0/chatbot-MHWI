import sqlite3
import os
import sys
from typing import Any, Dict, List, Optional
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

# Caminho para o banco de dados extraído do jogo (mhw.db)
if getattr(sys, 'frozen', False):
    DB_PATH = os.path.join(os.path.dirname(sys.executable), "mhw.db")
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "mhw.db")

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Please ensure mhw.db is downloaded.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_search_term(term):
    if not term: return ""
    term = term.lower().strip()
    replacements = {"alpha": "α", "beta": "β", "gamma": "γ", " a+": " α+", " b+": " β+", " g+": " γ+"}
    for k, v in replacements.items():
        if k in term: term = term.replace(k, v)
    return term.strip()

# Cache de imagens (URL)
MONSTER_IMAGE_CACHE = {}

def get_monster_image_url(monster_name):
    if not monster_name: return None
    cache_key = monster_name.lower().replace(" ", "_")
    if cache_key in MONSTER_IMAGE_CACHE: return MONSTER_IMAGE_CACHE[cache_key]

    try:
        formatted_name = monster_name.replace(" ", "+").title()
        url = f"https://monsterhunterworld.wiki.fextralife.com/{formatted_name}"
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            meta_image = soup.find('meta', property='og:image')
            if meta_image and meta_image.get('content'):
                image_url = meta_image['content']
                if "fextralife-logo" not in image_url and "http" in image_url:
                    MONSTER_IMAGE_CACHE[cache_key] = image_url
                    return image_url
    except Exception: pass
    return None

def get_monster_data(monster_name):
    conn = get_db_connection()
    try:
        # Se for Kulve, garantir busca pelo nome exato ou termo chave
        search = f"%{monster_name}%"
        if "taroth" in monster_name.lower() or "kulve" in monster_name.lower():
            search = "%Kulve Taroth%"

        query_monster = """
            SELECT m.id, m.size, t.name, t.ecology, t.description 
            FROM monster m
            JOIN monster_text t ON m.id = t.id
            WHERE t.name LIKE ? AND (t.lang_id = 'pt' OR t.lang_id = 'en')
            ORDER BY CASE WHEN t.lang_id = 'pt' THEN 0 ELSE 1 END
        """
        cursor = conn.execute(query_monster, (search,))
        monsters = cursor.fetchall()
        if not monsters: return None
            
        all_monster_info = []
        for monster in monsters:
            monster_id = monster['id']
            weakness_cols = {
                'fire': 'Fogo', 'water': 'Água', 'thunder': 'Trovão', 'ice': 'Gelo', 
                'dragon': 'Dragão', 'poison': 'Veneno', 'sleep': 'Sono', 
                'paralysis': 'Paralisia', 'blast': 'Explosão', 'stun': 'Atordoam.'
            }
            m_row = conn.execute("SELECT * FROM monster WHERE id = ?", (monster_id,)).fetchone()
            
            # Separar fraquezas (3-2 estrelas) e resistências (1-0 estrelas)
            weaknesses = []
            resistances = []
            
            for col, label in weakness_cols.items():
                val = m_row[f"weakness_{col}"]
                if val is not None:
                    if val >= 2:
                        weaknesses.append(f"{label}: {'★' * val} ({val})")
                    else:
                        resistances.append(f"{label}: {'★' * val if val > 0 else '✗'} ({val})")
            
            hitzone_query = """
                SELECT h.cut, h.impact, h.shot, h.fire, h.water, h.ice, h.thunder, h.dragon, h.ko, ht.name as part_name
                FROM monster_hitzone h
                JOIN monster_hitzone_text ht ON h.id = ht.id
                WHERE h.monster_id = ? AND (ht.lang_id = 'pt' OR ht.lang_id = 'en')
                ORDER BY h.id, CASE WHEN ht.lang_id = 'pt' THEN 0 ELSE 1 END
            """
            rows = conn.execute(hitzone_query, (monster_id,)).fetchall()
            hitzones = [{"part": r['part_name'], "cut": r['cut'], "impact": r['impact'], "shot": r['shot'], "fire": r['fire'], "water": r['water'], "ice": r['ice'], "thunder": r['thunder'], "dragon": r['dragon'], "ko": r['ko']} for r in rows]

            all_monster_info.append({
                "name": monster['name'], 
                "species": monster['ecology'], 
                "description": monster['description'], 
                "weaknesses": weaknesses,
                "resistances": resistances,
                "hitzones": hitzones, 
                "breaks": get_monster_breaks(conn, monster_id), 
                "rewards": get_monster_rewards(conn, monster_id)
            })
        return all_monster_info
    except Exception as e:
        print(f"Erro ao buscar dados no mhw.db: {e}")
        return []
    finally: conn.close()

def get_monster_rewards(conn, monster_id):
    try:
        query = """
            SELECT r.rank, r.condition_id, r.percentage, r.stack, it.name as item_name, ct.name as condition_name
            FROM monster_reward r
            JOIN item_text it ON r.item_id = it.id
            JOIN monster_reward_condition_text ct ON r.condition_id = ct.id
            WHERE r.monster_id = ? AND it.lang_id IN ('pt', 'en') AND ct.lang_id IN ('pt', 'en')
            ORDER BY r.rank, r.condition_id, r.percentage DESC
        """
        rows = conn.execute(query, (monster_id,)).fetchall()
        best_rewards = {}
        for row in rows:
            key = (row['rank'], row['item_name'])
            if key not in best_rewards or row['percentage'] > best_rewards[key]['chance']:
                best_rewards[key] = {"item": row['item_name'], "condition": row['condition_name'], "chance": row['percentage'], "stack": row['stack'], "rank": row['rank']}
        
        rewards = {}
        for data in best_rewards.values():
            rank = data.pop('rank')
            if rank not in rewards: rewards[rank] = []
            rewards[rank].append(data)
        for r in rewards: rewards[r].sort(key=lambda x: x['chance'], reverse=True)
        return rewards
    except Exception: return {}

def get_monster_breaks(conn, monster_id):
    try:
        # Se for Kulve Taroth (ID 51 ou similar), injetar partes do cerco se a tabela estiver vazia
        if monster_id == 51:
            return ["Chifres (Quebrar)", "Chifres (Escavar)", "Revestimento de Ouro (Peito)", "Revestimento de Ouro (Mãos)", "Revestimento de Ouro (Corpo)", "Cauda (Quebrar)"]

        # Tentar buscar partes quebráveis específicas
        query = """
            SELECT bt.name 
            FROM monster_break b 
            JOIN monster_break_text bt ON b.id = bt.id 
            WHERE b.monster_id = ? AND bt.lang_id IN ('pt', 'en')
        """
        rows = conn.execute(query, (monster_id,)).fetchall()
        if rows:
            return list(set(row[0] for row in rows))
        
        # Fallback via Hitzones
        query_hz = """
            SELECT DISTINCT ht.name 
            FROM monster_hitzone h 
            JOIN monster_hitzone_text ht ON h.id = ht.id 
            WHERE h.monster_id = ? AND ht.lang_id IN ('pt', 'en')
            AND (ht.name LIKE '%quebr%' OR ht.name LIKE '%cort%' OR ht.name LIKE '%escav%')
        """
        rows_hz = conn.execute(query_hz, (monster_id,)).fetchall()
        return [row[0] for row in rows_hz]
    except Exception: return []

# --- Equipamentos e Skills ---

def get_armor_info(armor_name):
    conn = get_db_connection()
    try:
        search_term = normalize_search_term(armor_name)
        query = """
            SELECT a.id, a.rarity, a.rank, a.armor_type, a.defense_base, a.defense_max, a.fire, a.water, a.thunder, a.ice, a.dragon, a.slot_1, a.slot_2, a.slot_3, at.name
            FROM armor a JOIN armor_text at ON a.id = at.id
            WHERE at.name LIKE ? AND at.lang_id IN ('pt', 'en')
            ORDER BY a.rank DESC, CASE WHEN at.lang_id = 'pt' THEN 0 ELSE 1 END
        """
        armors = conn.execute(query, (f"%{search_term}%",)).fetchall()
        results = []
        for row in armors:
            s_query = "SELECT st.name, ars.level FROM armor_skill ars JOIN skilltree_text st ON ars.skilltree_id = st.id WHERE ars.armor_id = ? AND st.lang_id = ?"
            skills = conn.execute(s_query, (row['id'], 'pt')).fetchall()
            if not skills: skills = conn.execute(s_query, (row['id'], 'en')).fetchall()
            slots = [row[s] for s in ['slot_1', 'slot_2', 'slot_3'] if row[s]]
            results.append({
                "name": row['name'], 
                "type": row['armor_type'], 
                "rank": row['rank'], 
                "defense": {"base": row['defense_base'], "max": row['defense_max']}, 
                "resistances": {
                    "fire": row['fire'], "water": row['water'], "thunder": row['thunder'], 
                    "ice": row['ice'], "dragon": row['dragon']
                },
                "slots": slots,
                "skills": [{"name": s[0], "level": s[1]} for s in skills]
            })
        return results
    except Exception: return []
    finally: conn.close()

def get_weapon_info(weapon_name):
    conn = get_db_connection()
    try:
        search_term = normalize_search_term(weapon_name)
        query = """
            SELECT w.id, w.weapon_type, w.rarity, w.attack, w.affinity, w.element1, w.element1_attack, w.slot_1, w.slot_2, w.slot_3, wt.name
            FROM weapon w JOIN weapon_text wt ON w.id = wt.id
            WHERE wt.name LIKE ? AND wt.lang_id IN ('pt', 'en')
            ORDER BY w.attack DESC, CASE WHEN wt.lang_id = 'pt' THEN 0 ELSE 1 END
        """
        weapons = conn.execute(query, (f"%{weapon_name}%",)).fetchall()
        results = []
        for row in weapons:
            slots = [row[s] for s in ['slot_1', 'slot_2', 'slot_3'] if row[s]]
            results.append({
                "name": row['name'], "type": row['weapon_type'], "rarity": row['rarity'], "attack": row['attack'], "affinity": row['affinity'],
                "element": {"type": row['element1'], "damage": row['element1_attack']} if row['element1'] else None, "slots": slots
            })
        return results
    except Exception: return []
    finally: conn.close()

def get_skill_info(skill_name):
    conn = get_db_connection()
    try:
        search_term = normalize_search_term(skill_name)
        query = """
            SELECT s.level, s.description, st.name
            FROM skill s JOIN skilltree_text st ON s.skilltree_id = st.id
            WHERE st.name LIKE ? AND st.lang_id IN ('pt', 'en')
            ORDER BY st.lang_id DESC, s.level
        """
        skills = conn.execute(query, (f"%{search_term}%",)).fetchall()
        if not skills: return None
        res = {"name": skills[0]['name'], "levels": []}
        for s in skills:
            if s['name'] == res['name']:
                res['levels'].append({"level": s['level'], "description": s['description']})
        return res
    except Exception: return None
    finally: conn.close()
def get_all_skill_max_levels():
    conn = get_db_connection()
    try:
        query = """
            SELECT st.name, MAX(s.level) as max_level
            FROM skill s
            JOIN skilltree_text st ON s.skilltree_id = st.id
            WHERE st.lang_id = 'pt'
            GROUP BY st.name
        """
        rows = conn.execute(query).fetchall()
        return {r['name']: r['max_level'] for r in rows}
    except Exception: return {}
    finally: conn.close()
