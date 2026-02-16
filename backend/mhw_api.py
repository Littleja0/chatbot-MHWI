import sqlite3
import os
import sys
from typing import Any, Dict, List, Optional
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

# Caminho para o banco de dados extraído do jogo (mhw.db)
if getattr(sys, 'frozen', False):
    # Se estiver rodando como executável (PyInstaller)
    DB_PATH = os.path.join(os.path.dirname(sys.executable), "mhw.db")
else:
    # Se estiver rodando como script normal
    DB_PATH = os.path.join(os.path.dirname(__file__), "mhw.db")

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Please ensure mhw.db is downloaded.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_search_term(term):
    """
    Normaliza termos de busca para equiparar com o banco de dados.
    Ex: 'beotodos b+' -> 'beo β+'
    """
    if not term: return ""
    term = term.lower().strip()
    
    # Map common typos/variations
    replacements = {
        "alpha": "α",
        "beta": "β",
        "gamma": "γ",
        " a+": " α+",
        " b+": " β+",
        " g+": " γ+",
    }
    
    # Do not remove stopwords or monster nicknames here as it might break exact DB matches
    # Just basic character normalization
    for k, v in replacements.items():
        if k in term:
            term = term.replace(k, v)
            
    return term.strip()

def get_all_monster_names():
    """Retorna lista de nomes de monstros para busca rápida."""
    conn = get_db_connection()
    try:
        # Pega nomes em PT e EN
        cursor = conn.execute("SELECT DISTINCT name FROM monster_text WHERE lang_id IN ('pt', 'en')")
        return [row[0] for row in cursor.fetchall() if row[0]]
    except Exception as e:
        print(f"Error getting monster names: {e}")
        return []
    finally:
        conn.close()

# Cache de imagens (URL)
MONSTER_IMAGE_CACHE = {}

def get_monster_image_url(monster_name):
    """
    Busca URL da imagem do monstro no Wiki Fextralife via scraping.
    Cacheia o resultado.
    """
    if not monster_name:
        return None

    # Tentar cache
    cache_key = monster_name.lower().replace(" ", "_")
    if cache_key in MONSTER_IMAGE_CACHE:
        return MONSTER_IMAGE_CACHE[cache_key]

    try:
        # Formatar nome para URL Wiki
        # Ex: Great Jagras -> Great+Jagras
        # Ex: Rathalos -> Rathalos
        formatted_name = monster_name.replace(" ", "+").title()
        
        url = f"https://monsterhunterworld.wiki.fextralife.com/{formatted_name}"
        
        # Timeout curto para não travar a API
        resp = requests.get(url, timeout=2)
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            meta_image = soup.find('meta', property='og:image')
            
            if meta_image and meta_image.get('content'):
                image_url = meta_image['content']
                # Validar imagem (não pegar logo default)
                if "fextralife-logo" not in image_url and "http" in image_url:
                    MONSTER_IMAGE_CACHE[cache_key] = image_url
                    return image_url

    except Exception as e:
        print(f"Erro scraping imagem {monster_name}: {e}")
    return None

def get_monster_data(monster_name):
    """
    Busca dados do monstro DIRETAMENTE do arquivo de dados do jogo (mhw.db).
    Retorna fraquezas (estrelas) e hitzones (valores de dano).
    """
    conn = get_db_connection()
    try:
        # 1. Buscar ID do monstro pelo nome (case insensitive)
        query_monster = """
            SELECT m.id, m.size, t.name, t.ecology, t.description 
            FROM monster m
            JOIN monster_text t ON m.id = t.id
            WHERE t.name LIKE ? AND (t.lang_id = 'pt' OR t.lang_id = 'en')
            ORDER BY CASE WHEN t.lang_id = 'pt' THEN 0 ELSE 1 END
        """
        cursor = conn.execute(query_monster, (f"%{monster_name}%",))
        monsters = cursor.fetchall()
        
        if not monsters:
            return None
            
        all_monster_info = []
        for monster in monsters:
            monster_id = monster['id']
            
            # 2. Buscar Fraquezas Gerais (Estrelas)
            weakness_cols = {
                'fire': 'Fogo', 'water': 'Água', 'thunder': 'Trovão', 'ice': 'Gelo',
                'dragon': 'Dragão', 'poison': 'Veneno', 'sleep': 'Sono', 
                'paralysis': 'Paralisia', 'blast': 'Explosão', 'stun': 'Atordoam.'
            }
            
            m_row = conn.execute("SELECT * FROM monster WHERE id = ?", (monster_id,)).fetchone()
            weaknesses = []
            for col, label in weakness_cols.items():
                val = m_row[f"weakness_{col}"]
                if val and val >= 2:
                    stars = "★" * val
                    weaknesses.append(f"{label}: {stars} ({val})")
            
            # 3. Buscar Hitzones
            hitzone_query = """
                SELECT h.cut, h.impact, h.shot, h.fire, h.water, h.ice, h.thunder, h.dragon, h.ko,
                       ht.name as part_name
                FROM monster_hitzone h
                JOIN monster_hitzone_text ht ON h.id = ht.id
                WHERE h.monster_id = ? AND ht.lang_id = 'pt'
                ORDER BY h.id
            """
            rows = conn.execute(hitzone_query, (monster_id,)).fetchall()
            if not rows:
                rows = conn.execute(hitzone_query.replace("'pt'", "'en'"), (monster_id,)).fetchall()

            hitzones = []
            for row in rows:
                hitzones.append({
                    "part": row['part_name'], "cut": row['cut'], "impact": row['impact'],
                    "shot": row['shot'], "fire": row['fire'], "water": row['water'],
                    "ice": row['ice'], "thunder": row['thunder'], "dragon": row['dragon'], "ko": row['ko']
                })

            all_monster_info.append({
                "name": monster['name'],
                "species": monster['ecology'], 
                "description": monster['description'],
                "weaknesses": weaknesses,
                "hitzones": hitzones,
                "breaks": get_monster_breaks(conn, monster_id),
                "rewards": get_monster_rewards(conn, monster_id)
            })
        return all_monster_info
    except Exception as e:
        print(f"Erro ao buscar dados no mhw.db: {e}")
        return []
    finally:
        conn.close()

def get_monster_rewards(conn, monster_id):
    """
    Busca drops/recompensas do monstro.
    """
    try:
        query = """
            SELECT r.rank, r.condition_id, r.percentage, r.stack,
                   it.name as item_name,
                   ct.name as condition_name
            FROM monster_reward r
            JOIN item_text it ON r.item_id = it.id
            JOIN monster_reward_condition_text ct ON r.condition_id = ct.id
            WHERE r.monster_id = ? 
              AND it.lang_id = 'pt'
              AND ct.lang_id = 'pt'
            ORDER BY r.rank, r.condition_id, r.percentage DESC
        """
        # Fallback to English if PT is missing (common in some DB versions for newer items)
        cursor = conn.execute(query, (monster_id,))
        rows = cursor.fetchall()
        
        if not rows:
             query_en = query.replace("'pt'", "'en'")
             cursor = conn.execute(query_en, (monster_id,))
             rows = cursor.fetchall()

        # Agrupar e deduplicar para mostrar itens únicos com a melhor chance
        rewards = {}
        # (rank, item_name) -> melhor_recompensa
        best_rewards = {}

        for row in rows:
            rank = row['rank']
            item_name = row['item_name']
            chance = row['percentage']
            
            key = (rank, item_name)
            if key not in best_rewards or chance > best_rewards[key]['chance']:
                best_rewards[key] = {
                    "item": item_name,
                    "condition": row['condition_name'],
                    "chance": chance,
                    "stack": row['stack']
                }

        # Organizar de volta no dicionário por Rank
        for (rank, item_name), data in best_rewards.items():
            if rank not in rewards:
                rewards[rank] = []
            rewards[rank].append(data)
            
        # Ordenar por maior chance dentro de cada Rank
        for r in rewards:
            rewards[r].sort(key=lambda x: x['chance'], reverse=True)
            
        return rewards
    except Exception as e:
        print(f"Erro rewards: {e}")
        return {}

def get_monster_breaks(conn, monster_id):
    """
    Busca partes quebráveis/cortáveis do monstro.
    """
    try:
        query = """
            SELECT bt.name
            FROM monster_break b
            JOIN monster_break_text bt ON b.id = bt.id
            WHERE b.monster_id = ? AND bt.lang_id = 'pt'
        """
        cursor = conn.execute(query, (monster_id,))
        rows = cursor.fetchall()
        if not rows:
             rows = conn.execute(query.replace("'pt'", "'en'"), (monster_id,)).fetchall()
        
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Erro breaks: {e}")
        return []

def get_item_info(item_name):
    """
    Busca informações de item no mhw.db
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT i.*, t.name, t.description 
            FROM item i
            JOIN item_text t ON i.id = t.id
            WHERE t.name LIKE ? AND (t.lang_id = 'pt' OR t.lang_id = 'en')
            ORDER BY t.lang_id DESC
        """
        rows = conn.execute(query, (f"%{item_name}%",)).fetchall()
        
        results = []
        for row in rows:
            results.append({
                "name": row['name'],
                "description": row['description'],
                "rarity": row['rarity'],
                "carry_limit": row['carry_limit'],
                "buy_price": row['buy_price'],
                "sell_price": row['sell_price']
            })
        return results
    except Exception as e:
        print(f"Erro item: {e}")
        return []
    finally:
        conn.close()


def get_armor_info(armor_name):
    """
    Busca informações de uma peça de armadura específica no mhw.db
    Inclui defesa, resistências, skills e slots.
    """
    conn = get_db_connection()
    try:
        # Search Term normalization
        search_term = normalize_search_term(armor_name)
        
        # Buscar armadura pelo nome
        query = """
            SELECT a.id, a.rarity, a.rank, a.armor_type,
                   a.defense_base, a.defense_max, a.defense_augment_max,
                   a.fire, a.water, a.thunder, a.ice, a.dragon,
                   a.slot_1, a.slot_2, a.slot_3,
                   at.name, at.lang_id
            FROM armor a
            JOIN armor_text at ON a.id = at.id
            WHERE at.name LIKE ? 
            ORDER BY a.rank DESC, CASE WHEN at.lang_id = 'pt' THEN 0 ELSE 1 END
        """
        armors = conn.execute(query, (f"%{search_term}%",)).fetchall()
        
        if not armors:
            if search_term != armor_name:
                 armors = conn.execute(query, (f"%{armor_name}%",)).fetchall()
            
        if not armors:
            return None
        
        all_armor_info = []
        for armor_row in armors:
            armor_id = armor_row['id']
            # Para cada peça, precisamos buscar as skills e traduzir se necessário
            
            # Buscar skills da armadura
            skills_query = """
                SELECT st.name as skill_name, ars.level
                FROM armor_skill ars
                JOIN skilltree_text st ON ars.skilltree_id = st.id
                WHERE ars.armor_id = ? AND st.lang_id = 'pt'
            """
            skills = conn.execute(skills_query, (armor_id,)).fetchall()
            if not skills:
                skills = conn.execute(skills_query.replace("'pt'", "'en'"), (armor_id,)).fetchall()
            
            # Formatar slots
            slots = []
            for s_key in ['slot_1', 'slot_2', 'slot_3']:
                if armor_row[s_key]: slots.append(armor_row[s_key])
            
            armor_type_map = {
                'head': 'Capacete', 'chest': 'Peitoral', 'arms': 'Braços',
                'waist': 'Cintura', 'legs': 'Pernas'
            }
            
            all_armor_info.append({
                "name": armor_row['name'],
                "type": armor_type_map.get(armor_row['armor_type'], armor_row['armor_type']),
                "rarity": armor_row['rarity'],
                "rank": armor_row['rank'],
                "defense": {
                    "base": armor_row['defense_base'],
                    "max": armor_row['defense_max'],
                    "augmented": armor_row['defense_augment_max']
                },
                "resistances": {
                    "fire": armor_row['fire'], "water": armor_row['water'],
                    "thunder": armor_row['thunder'], "ice": armor_row['ice'],
                    "dragon": armor_row['dragon']
                },
                "slots": slots,
                "skills": [{"name": s['skill_name'], "level": s['level']} for s in skills]
            })
            
        return all_armor_info
        
    except Exception as e:
        print(f"Erro armor: {e}")
        return []
    finally:
        conn.close()




def get_armor_set(set_name):
    """
    Busca peças de armadura agrupadas por Set Name e Rank.
    """
    conn = get_db_connection()
    try:
        # Normalize search term
        original_term = set_name
        search_term = normalize_search_term(set_name)
        
        # Query base
        query = """
            SELECT DISTINCT a.id, a.rarity, a.rank, a.armor_type,
                   a.defense_base, a.defense_max, a.defense_augment_max,
                   a.fire, a.water, a.thunder, a.ice, a.dragon,
                   a.slot_1, a.slot_2, a.slot_3,
                   at.name, at.lang_id,
                   ast.name as armorset_name
            FROM armor a
            JOIN armor_text at ON a.id = at.id
            LEFT JOIN armorset ars ON a.armorset_id = ars.id
            LEFT JOIN armorset_text ast ON ars.id = ast.id AND ast.lang_id = at.lang_id
            WHERE (at.name LIKE ? OR ast.name LIKE ?)
              AND at.lang_id IN ('pt', 'en')
            ORDER BY a.rank, ast.name, a.rarity, 
                     CASE a.armor_type 
                         WHEN 'head' THEN 1 
                         WHEN 'chest' THEN 2 
                         WHEN 'arms' THEN 3 
                         WHEN 'waist' THEN 4 
                         WHEN 'legs' THEN 5 
                     END
        """
        
        # Try normalized search first
        pieces = conn.execute(query, (f"%{search_term}%", f"%{search_term}%")).fetchall()
        
        # Fallback: Try with original prompt if normalized failed (just in case)
        if not pieces and search_term != original_term:
             pieces = conn.execute(query, (f"%{original_term}%", f"%{original_term}%")).fetchall()
        
        # Smart search fallback (Splitting words)
        if not pieces:
            search_terms: list[str] = []
            
            # Use normalized term for split logic
            split_source = search_term if len(search_term) > 3 else original_term
            
            if '-' in split_source:
                search_terms.extend(split_source.split('-'))
            if ' ' in split_source:
                search_terms.extend(split_source.split(' '))
            
            # Subspecies specific logic
            if "viper" in split_source.lower() or "vipero" in split_source.lower():
                search_terms.insert(0, "Vípero")
                search_terms.insert(0, "Viper")
            
            # Filter short terms and generic words
            exclude_terms = ['β+', 'α+', 'γ+', 'set', 'elmo', 'helm', 'capacete', 'peitoral', 'braços', 'cintura', 'pernas', 'amuleto', 'arma']
            valid_terms = [t for t in search_terms if len(t) >= 3 and t.lower() not in exclude_terms]
            
            for term in valid_terms:
                 # print(f"Trying term: {term}")
                 p = conn.execute(query, (f"%{term}%", f"%{term}%")).fetchall()
                 if p:
                     pieces = p
                     # print(f"[armor_set] Found via '{term}'")
                     break
        
        if not pieces:
            return None
        
        # Group by Set Name + Rank to avoid mixing "Kadachi" and "Viper Kadachi"
        grouped_sets = {}
        
        # Deduplicate by ID, preferring PT
        unique_pieces = {}
        for p in pieces:
            p_id = p['id']
            lang = p['lang_id']
            
            # If new ID, add it
            if p_id not in unique_pieces:
                unique_pieces[p_id] = p
            else:
                # If existing is EN and new is PT, replace
                if unique_pieces[p_id]['lang_id'] != 'pt' and lang == 'pt':
                    unique_pieces[p_id] = p
        
        # Enrich with PT translation if we only have EN
        # This handles cases where user search matches EN name only, but we want to display PT
        for p_id, piece in unique_pieces.items():
            if piece['lang_id'] != 'pt':
                try:
                    pt_trans = conn.execute("SELECT name FROM armor_text WHERE id = ? AND lang_id = 'pt'", (p_id,)).fetchone()
                    if pt_trans:
                        # Create a modifiable copy (Rows are immutable usually)
                        # Actually sqlite3.Row fits strict mapping, lets convert to dict slightly or just patch name
                        # Since we build a new dict below, we can just patch a "display_name" or update the logic below
                        # to use translation.
                        # Let's store translation in a sidecar or just update the object if it was a dict (it is a Row)
                        # We can't update Row.
                        # Let's add to a translation map
                        piece_trans = dict(piece) # Convert Row to dict to allow edit
                        piece_trans['name'] = pt_trans['name']
                        piece_trans['lang_id'] = 'pt'
                        unique_pieces[p_id] = piece_trans
                except:
                    pass

        # Convert back to list sorted by original sort order (approx)
        # Actually we lost order. Let's sort by rank, rarity, type.
        final_pieces = sorted(unique_pieces.values(), key=lambda x: (
            x['rank'], 
            x['rarity'],
            {'head': 1, 'chest': 2, 'arms': 3, 'waist': 4, 'legs': 5}.get(x['armor_type'], 6)
        ))
        
        # Group by set
        sets = {}
        for piece in final_pieces:
            # Armorset Name might be None or varied
            set_name_display = piece['armorset_name'] if piece['armorset_name'] else "Unknown Set"
            rank = piece['rank']
            key = (set_name_display, rank)
            
            if key not in sets:
                sets[key] = []
            
            # Get skills (Language handling needed here too?)
            # Skills query is separate usually? No, skills attached to piece?
            # The current code fetches skills per piece inside loop? No, it's not shown here.
            # Assuming query returns piece data, we need skills.
            
            # Helper to get skills for a piece
            piece_skills = []
            try:
                s_query = """
                    SELECT st.name as skill_name, aps.level
                    FROM armor_skill aps
                    JOIN skilltree_text st ON aps.skilltree_id = st.id
                    WHERE aps.armor_id = ? AND st.lang_id = 'pt'
                """
                s_rows = conn.execute(s_query, (piece['id'],)).fetchall()
                if not s_rows:
                    # Fallback to EN if PT missing
                    s_query_en = """
                        SELECT st.name as skill_name, aps.level
                        FROM armor_skill aps
                        JOIN skilltree_text st ON aps.skilltree_id = st.id
                        WHERE aps.armor_id = ? AND st.lang_id = 'en'
                    """
                    s_rows = conn.execute(s_query_en, (piece['id'],)).fetchall()
                
                piece_skills = [{"name": s['skill_name'], "level": s['level']} for s in s_rows]
            except:
                pass

            # Calculate slots
            slots = []
            if piece['slot_1']: slots.append(piece['slot_1'])
            if piece['slot_2']: slots.append(piece['slot_2'])
            if piece['slot_3']: slots.append(piece['slot_3'])

            sets[key].append({
                "name": piece['name'],
                "type": piece['armor_type'],
                "rarity": piece['rarity'],
                "defense": piece['defense_base'],
                "resistances": {
                   "fire": piece['fire'], "water": piece['water'], "thunder": piece['thunder'], "ice": piece['ice'], "dragon": piece['dragon']
                },
                "slots": slots,
                "lang_id": piece['lang_id'],
                "skills": piece_skills
            })
        
        result: Dict[str, Any] = {
            "search_term": search_term,
            "sets": []
        }
        
        for (s_name, s_rank), s_pieces in sets.items():
            result["sets"].append({
                "name": s_name,
                "rank": s_rank,
                "pieces": s_pieces
            })
        
        # Helper to sort ranks LR < HR < MR
        rank_order = {'LR': 1, 'HR': 2, 'MR': 3}
        result["sets"].sort(key=lambda x: (rank_order.get(x['rank'], 0), x['name']))
        
        return result

    except Exception as e:
        print(f"Erro armor set: {e}")
        return None
    finally:
        conn.close()


def get_all_armor_names():
    """Retorna lista de nomes de armaduras para busca."""
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            SELECT DISTINCT name FROM armor_text 
            WHERE lang_id IN ('pt', 'en')
            ORDER BY name
        """)
        return [row[0] for row in cursor.fetchall() if row[0]]
    except Exception as e:
        print(f"Error getting armor names: {e}")
        return []
    finally:
        conn.close()


def search_equipment(search_term):
    """
    Busca geral por equipamentos (armaduras, armas, itens).
    Retorna o tipo e dados do equipamento encontrado.
    """
    # Tentar armadura primeiro
    armor = get_armor_info(search_term)
    if armor:
        return {"type": "armor", "data": armor}
    
    # Tentar set de armadura
    armor_set = get_armor_set(search_term)
    if armor_set and armor_set.get('sets'):
        return {"type": "armor_set", "data": armor_set}
    
    # Tentar adorno
    deco = get_decoration_info(search_term)
    if deco:
        return {"type": "decoration", "data": deco}
    
    # Tentar amuleto
    charm = get_charm_info(search_term)
    if charm:
        return {"type": "charm", "data": charm}
    
    # Tentar arma
    weapon = get_weapon_info(search_term)
    if weapon:
        return {"type": "weapon", "data": weapon}
    
    # Tentar ferramenta/manto
    tool = get_tool_info(search_term)
    if tool:
        return {"type": "tool", "data": tool}
    
    # Tentar item
    item = get_item_info(search_term)
    if item:
        return {"type": "item", "data": item}
    
    return None


# ========== ADORNOS (Decorations/Jewels) ==========

def get_decoration_info(deco_name):
    """
    Busca informações de um adorno/joia.
    """
    conn = get_db_connection()
    try:
        deco_name = normalize_search_term(deco_name)
        
        query = """
            SELECT d.id, d.rarity, d.slot, d.skilltree_id, d.skilltree_level,
                   dt.name, st.name as skill_name
            FROM decoration d
            JOIN decoration_text dt ON d.id = dt.id
            LEFT JOIN skilltree_text st ON d.skilltree_id = st.id AND st.lang_id = dt.lang_id
            WHERE dt.name LIKE ?
            ORDER BY d.slot DESC, CASE WHEN dt.lang_id = 'pt' THEN 0 ELSE 1 END
        """
        decos = conn.execute(query, (f"%{deco_name}%",)).fetchall()
        
        if not decos:
            return None
        
        all_decos = []
        for deco in decos:
            all_decos.append({
                "name": deco['name'],
                "rarity": deco['rarity'],
                "slot_size": deco['slot'],
                "skill": deco['skill_name'],
                "skill_level": deco['skilltree_level']
            })
        return all_decos
    except Exception as e:
        print(f"Erro decoration: {e}")
        return []
    finally:
        conn.close()


def get_all_decorations():
    """Retorna lista de todos os adornos."""
    conn = get_db_connection()
    try:
        query = """
            SELECT d.id, d.rarity, d.slot, dt.name, st.name as skill_name, d.skilltree_level
            FROM decoration d
            JOIN decoration_text dt ON d.id = dt.id
            LEFT JOIN skilltree_text st ON d.skilltree_id = st.id AND st.lang_id = 'pt'
            WHERE dt.lang_id = 'pt'
            ORDER BY d.slot, d.rarity
        """
        rows = conn.execute(query).fetchall()
        return [{
            "name": r['name'],
            "rarity": r['rarity'],
            "slot": r['slot'],
            "skill": r['skill_name'],
            "level": r['skilltree_level']
        } for r in rows]
    except Exception as e:
        print(f"Error getting all decorations: {e}")
        return []
    finally:
        conn.close()


# ========== AMULETOS (Charms) ==========

def get_charm_info(charm_name):
    """
    Busca informações de um amuleto.
    """
    conn = get_db_connection()
    try:
        charm_name = normalize_search_term(charm_name)

        query = """
            SELECT c.id, c.rarity, ct.name
            FROM charm c
            JOIN charm_text ct ON c.id = ct.id
            WHERE ct.name LIKE ?
            ORDER BY CASE WHEN ct.lang_id = 'pt' THEN 0 ELSE 1 END
            LIMIT 1
        """
        charm = conn.execute(query, (f"%{charm_name}%",)).fetchone()
        
        if not charm:
            return None
        
        charm_id = charm['id']
        
        # Buscar skills do amuleto
        skills_query = """
            SELECT st.name as skill_name, cs.level
            FROM charm_skill cs
            JOIN skilltree_text st ON cs.skilltree_id = st.id
            WHERE cs.charm_id = ? AND st.lang_id = 'pt'
        """
        skills = conn.execute(skills_query, (charm_id,)).fetchall()
        
        return {
            "name": charm['name'],
            "rarity": charm['rarity'],
            "skills": [{"name": s['skill_name'], "level": s['level']} for s in skills]
        }
    except Exception as e:
        print(f"Erro charm: {e}")
        return None
    finally:
        conn.close()


def get_charm_upgrades(charm_name):
    """
    Busca TODOS os níveis de um amuleto (I, II, III, IV, V).
    Inclui skills e materiais de crafting.
    """
    conn = get_db_connection()
    try:
        # Remover números romanos se presentes para buscar o nome base
        base_name = charm_name
        for suffix in [' I', ' II', ' III', ' IV', ' V', ' VI', ' VII']:
            base_name = base_name.replace(suffix, '')
        
        # Buscar todos os amuletos com esse nome base
        query = """
            SELECT DISTINCT c.id, c.rarity, c.recipe_id, c.previous_id, ct.name, ct.lang_id
            FROM charm c
            JOIN charm_text ct ON c.id = ct.id
            WHERE ct.name LIKE ?
            ORDER BY c.rarity, ct.lang_id
        """
        charms = conn.execute(query, (f"%{base_name}%",)).fetchall()
        
        if not charms:
            return None
        
        # Agrupar por idioma preferencial (PT > EN)
        seen_ids = set()
        results = []
        
        for charm in charms:
            if charm['id'] in seen_ids:
                continue
            seen_ids.add(charm['id'])
            
            # Buscar skills
            skills_query = """
                SELECT st.name as skill_name, cs.level
                FROM charm_skill cs
                JOIN skilltree_text st ON cs.skilltree_id = st.id
                WHERE cs.charm_id = ? AND st.lang_id = 'pt'
            """
            skills = conn.execute(skills_query, (charm['id'],)).fetchall()
            
            # Buscar materiais de crafting
            materials = []
            if charm['recipe_id']:
                materials_query = """
                    SELECT it.name, ri.quantity
                    FROM recipe_item ri
                    JOIN item_text it ON ri.item_id = it.id
                    WHERE ri.recipe_id = ? AND it.lang_id = 'pt'
                """
                mats = conn.execute(materials_query, (charm['recipe_id'],)).fetchall()
                materials = [{"name": m['name'], "quantity": m['quantity']} for m in mats]
            
            results.append({
                "name": charm['name'],
                "rarity": charm['rarity'],
                "skills": [{"name": s['skill_name'], "level": s['level']} for s in skills],
                "materials": materials
            })
        
        # Ordenar por rarity (para mostrar I, II, III em ordem)
        results.sort(key=lambda x: x['rarity'])
        
        return {
            "base_name": base_name,
            "upgrades": results
        }
    except Exception as e:
        print(f"Erro charm upgrades: {e}")
        return None
    finally:
        conn.close()

# ========== MISSÕES (Quests) ==========

def get_quest_info(quest_name):
    """
    Busca informações de uma missão.
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT q.id, q.category, q.rank, q.stars, q.quest_type, q.zenny,
                   qt.name, qt.objective, qt.description
            FROM quest q
            JOIN quest_text qt ON q.id = qt.id
            WHERE qt.name LIKE ?
            ORDER BY q.stars, CASE WHEN qt.lang_id = 'pt' THEN 0 ELSE 1 END
        """
        quests = conn.execute(query, (f"%{quest_name}%",)).fetchall()
        
        results = []
        for quest in quests:
            quest_id = quest['id']
            # Buscar monstros da missão
            monsters_query = """
                SELECT mt.name, qm.quantity
                FROM quest_monster qm
                JOIN monster_text mt ON qm.monster_id = mt.id
                WHERE qm.quest_id = ? AND mt.lang_id = 'pt'
            """
            monsters = conn.execute(monsters_query, (quest_id,)).fetchall()
            
            # Buscar recompensas
            rewards_query = """
                SELECT it.name, qr.percentage, qr.stack
                FROM quest_reward qr
                JOIN item_text it ON qr.item_id = it.id
                WHERE qr.quest_id = ? AND it.lang_id = 'pt'
                ORDER BY qr.percentage DESC
                LIMIT 10
            """
            rewards = conn.execute(rewards_query, (quest_id,)).fetchall()
            
            results.append({
                "name": quest['name'],
                "category": quest['category'],
                "rank": quest['rank'],
                "stars": quest['stars'],
                "type": quest['quest_type'],
                "zenny": quest['zenny'],
                "objective": quest['objective'],
                "description": quest['description'],
                "monsters": [{"name": m['name'], "quantity": m['quantity']} for m in monsters],
                "rewards": [{"item": r['name'], "chance": r['percentage'], "stack": r['stack']} for r in rewards]
            })
        return results
    except Exception as e:
        print(f"Erro quest: {e}")
        return []
    finally:
        conn.close()


def search_quests_by_monster(monster_name):
    """
    Busca missões que contêm um monstro específico.
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT DISTINCT q.id, q.rank, q.stars, qt.name
            FROM quest q
            JOIN quest_text qt ON q.id = qt.id
            JOIN quest_monster qm ON q.id = qm.quest_id
            JOIN monster_text mt ON qm.monster_id = mt.id
            WHERE mt.name LIKE ? AND qt.lang_id = 'pt'
            ORDER BY q.stars
        """
        quests = conn.execute(query, (f"%{monster_name}%",)).fetchall()
        
        return [{
            "name": q['name'],
            "rank": q['rank'],
            "stars": q['stars']
        } for q in quests]
    except Exception as e:
        print(f"Error searching quests: {e}")
        return []
    finally:
        conn.close()


# ========== FERRAMENTAS/MANTOS (Tools/Mantles) ==========

def get_tool_info(tool_name):
    """
    Busca informações de uma ferramenta especializada ou manto.
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT t.id, t.tool_type, t.duration, t.duration_upgraded, 
                   t.recharge, t.slot_1, t.slot_2, t.slot_3,
                   tt.name, tt.description
            FROM tool t
            JOIN tool_text tt ON t.id = tt.id
            WHERE tt.name LIKE ?
            ORDER BY CASE WHEN tt.lang_id = 'pt' THEN 0 ELSE 1 END
        """
        rows = conn.execute(query, (f"%{tool_name}%",)).fetchall()
        
        results = []
        for tool in rows:
            slots = []
            if tool['slot_1']: slots.append(tool['slot_1'])
            if tool['slot_2']: slots.append(tool['slot_2'])
            if tool['slot_3']: slots.append(tool['slot_3'])
            
            results.append({
                "name": tool['name'],
                "type": tool['tool_type'],
                "duration": tool['duration'],
                "duration_upgraded": tool['duration_upgraded'],
                "recharge": tool['recharge'],
                "slots": slots,
                "description": tool['description']
            })
        return results
    except Exception as e:
        print(f"Erro tool: {e}")
        return []
    finally:
        conn.close()


def get_all_tools():
    """Retorna lista de todas as ferramentas/mantos."""
    conn = get_db_connection()
    try:
        query = """
            SELECT t.id, t.tool_type, t.duration, t.recharge, tt.name
            FROM tool t
            JOIN tool_text tt ON t.id = tt.id
            WHERE tt.lang_id = 'pt'
            ORDER BY t.id
        """
        rows = conn.execute(query).fetchall()
        return [{
            "name": r['name'],
            "type": r['tool_type'],
            "duration": r['duration'],
            "recharge": r['recharge']
        } for r in rows]
    except Exception as e:
        print(f"Error getting all tools: {e}")
        return []
    finally:
        conn.close()


# ========== ARMAS (Weapons) ==========

def get_weapon_info(weapon_name):
    """
    Busca informações de uma arma.
    """
    conn = get_db_connection()
    try:
        weapon_name = normalize_search_term(weapon_name)
        
        query = """
            SELECT w.id, w.weapon_type, w.rarity, w.attack, w.affinity, 
                   w.defense, w.element1, w.element1_attack, w.element2, w.element2_attack,
                   w.element_hidden, w.sharpness, w.sharpness_maxed,
                   w.slot_1, w.slot_2, w.slot_3, w.elderseal,
                   wt.name
            FROM weapon w
            JOIN weapon_text wt ON w.id = wt.id
            WHERE wt.name LIKE ?
            ORDER BY w.attack DESC, CASE WHEN wt.lang_id = 'pt' THEN 0 ELSE 1 END
        """
        weapons = conn.execute(query, (f"%{weapon_name}%",)).fetchall()
        
        if not weapons:
            return None
        
        all_weapons = []
        for weapon in weapons:
            weapon_id = weapon['id']
            
            # Buscar skills da arma (se houver)
            skills_query = """
                SELECT st.name as skill_name, ws.level
                FROM weapon_skill ws
                JOIN skilltree_text st ON ws.skilltree_id = st.id
                WHERE ws.weapon_id = ? AND st.lang_id = 'pt'
            """
            skills = conn.execute(skills_query, (weapon_id,)).fetchall()
            
            slots = []
            if weapon['slot_1']: slots.append(weapon['slot_1'])
            if weapon['slot_2']: slots.append(weapon['slot_2'])
            if weapon['slot_3']: slots.append(weapon['slot_3'])
            
            # Formatar elemento
            element = None
            if weapon['element1']:
                element = {
                    "type": weapon['element1'],
                    "damage": weapon['element1_attack'],
                    "hidden": weapon['element_hidden'] == 1
                }
            
            all_weapons.append({
                "name": weapon['name'],
                "type": weapon['weapon_type'],
                "rarity": weapon['rarity'],
                "attack": weapon['attack'],
                "affinity": weapon['affinity'],
                "defense": weapon['defense'],
                "element": element,
                "elderseal": weapon['elderseal'],
                "slots": slots,
                "sharpness": weapon['sharpness'],
                "skills": [{"name": s['skill_name'], "level": s['level']} for s in skills]
            })
        return all_weapons
    except Exception as e:
        print(f"Erro weapon: {e}")
        return []
    finally:
        conn.close()


def search_weapons_by_type(weapon_type):
    """
    Busca armas por tipo (great-sword, long-sword, etc.)
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT w.id, w.weapon_type, w.rarity, w.attack, w.affinity, wt.name
            FROM weapon w
            JOIN weapon_text wt ON w.id = wt.id
            WHERE w.weapon_type LIKE ? AND wt.lang_id = 'pt'
            ORDER BY w.rarity DESC, w.attack DESC
            LIMIT 50
        """
        weapons = conn.execute(query, (f"%{weapon_type}%",)).fetchall()
        
        return [{
            "name": w['name'],
            "type": w['weapon_type'],
            "rarity": w['rarity'],
            "attack": w['attack'],
            "affinity": w['affinity']
        } for w in weapons]
    except Exception as e:
        print(f"Error searching weapons by type: {e}")
        return []
    finally:
        conn.close()


# ========== KINSECTS (Insect Glaive) ==========

def get_kinsect_info(kinsect_name):
    """
    Busca informações de um Kinsect (para Glaive Inseto).
    """
    conn = get_db_connection()
    try:
        kinsect_name = normalize_search_term(kinsect_name)
        
        query = """
            SELECT k.id, k.rarity, k.attack_type, k.dust_effect, 
                   k.power, k.speed, k.heal,
                   kt.name
            FROM kinsect k
            JOIN kinsect_text kt ON k.id = kt.id
            WHERE kt.name LIKE ?
            ORDER BY k.rarity DESC, CASE WHEN kt.lang_id = 'pt' THEN 0 ELSE 1 END
        """
        rows = conn.execute(query, (f"%{kinsect_name}%",)).fetchall()
        
        results = []
        for kinsect in rows:
            results.append({
                "name": kinsect['name'],
                "rarity": kinsect['rarity'],
                "attack_type": kinsect['attack_type'],
                "dust_effect": kinsect['dust_effect'],
                "power": kinsect['power'],
                "speed": kinsect['speed'],
                "heal": kinsect['heal']
            })
        return results
    except Exception as e:
        print(f"Erro kinsect: {e}")
        return []
    finally:
        conn.close()


# ========== SKILLS ==========

def get_skill_info(skill_name):
    """
    Busca informações de uma skill.
    Tenta PT primeiro, fallback para EN.
    """
    conn = get_db_connection()
    try:
        skill_name = normalize_search_term(skill_name)

        # Tentar português primeiro
        for lang in ['pt', 'en']:
            query = """
                SELECT s.skilltree_id, s.level, s.description, st.name
                FROM skill s
                JOIN skilltree_text st ON s.skilltree_id = st.id
                WHERE st.name LIKE ? AND st.lang_id = ?
                ORDER BY s.level
            """
            skills = conn.execute(query, (f"%{skill_name}%", lang)).fetchall()
            
            if skills:
                break
        
        if not skills:
            return None
        
        levels = []
        found_skill_name = None
        for s in skills:
            s_name = s['name']
            if not found_skill_name:
                found_skill_name = s_name
            levels.append({
                "level": s['level'],
                "description": s['description']
            })
        
        return {
            "name": found_skill_name,
            "levels": levels,
            "max_level": len(levels)
        }
    except Exception as e:
        print(f"Erro skill: {e}")
        return None
    finally:
        conn.close()


# ========== BUSCA GERAL EXPANDIDA ==========

def search_all(search_term):
    """
    Busca em todos os tipos de dados do jogo.
    Retorna uma lista de resultados consolidados.
    """
    results = []
    
    # Mapeamento de funções de busca
    search_funcs = [
        ("monster", get_monster_data),
        ("armor", get_armor_info),
        ("armor_set", get_armor_set), # Get_armor_set returns a dict with "sets" key
        ("weapon", get_weapon_info),
        ("decoration", get_decoration_info),
        ("charm", get_charm_info),
        ("quest", get_quest_info),
        ("tool", get_tool_info),
        ("skill", get_skill_info),
        ("item", get_item_info)
    ]
    
    for data_type, func in search_funcs:
        try:
            res = func(search_term)
            if not res:
                continue
                
            if isinstance(res, list):
                for item in res:
                    results.append({"type": data_type, "data": item})
            elif data_type == "armor_set" and "sets" in res:
                results.append({"type": data_type, "data": res})
            else:
                results.append({"type": data_type, "data": res})
        except Exception as e:
            print(f"Erro na busca geral ({data_type}) para '{search_term}': {e}")
            
    return results
