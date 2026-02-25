import sqlite3
import json
from typing import List, Optional, Any, Dict
from core.config import MHW_DB_PATH

# === Global Normalization Maps ===

WEAPON_MAP = {
    "gs": "Great Sword", "greatsword": "Great Sword", "espadão": "Great Sword", "espadao": "Great Sword",
    "ls": "Long Sword", "longsword": "Long Sword", "katana": "Long Sword", "espada longa": "Long Sword",
    "sns": "Sword & Shield", "sword and shield": "Sword & Shield", "espada e escudo": "Sword & Shield",
    "db": "Dual Blades", "dualblades": "Dual Blades", "duals": "Dual Blades", "lâminas duplas": "Dual Blades", "laminas duplas": "Dual Blades",
    "hammer": "Hammer", "martelo": "Hammer",
    "hh": "Hunting Horn", "huntinghorn": "Hunting Horn", "corneta": "Hunting Horn", "bumbo": "Hunting Horn", "flauta": "Hunting Horn",
    "lance": "Lance", "lança": "Lance",
    "gl": "Gunlance", "gunlance": "Gunlance", "lança-fuzil": "Gunlance", "lanca-fuzil": "Gunlance",
    "sa": "Switch Axe", "switchaxe": "Switch Axe", "transmachado": "Switch Axe",
    "cb": "Charge Blade", "chargeblade": "Charge Blade", "lâmina carregada": "Charge Blade", "lamina carregada": "Charge Blade",
    "ig": "Insect Glaive", "insectglaive": "Insect Glaive", "glaive": "Insect Glaive", "glaive inseto": "Insect Glaive",
    "lbg": "Light Bowgun", "lightbowgun": "Light Bowgun", "fuzil leve": "Light Bowgun",
    "hbg": "Heavy Bowgun", "heavybowgun": "Heavy Bowgun", "fuzil pesado": "Heavy Bowgun",
    "bow": "Bow", "arco": "Bow"
}

TYPE_PT_MAP = {
    "great-sword": "Espadão",
    "long-sword": "Espada Longa (Katana)",
    "sword-and-shield": "Espada e Escudo",
    "dual-blades": "Lâminas Duplas",
    "hammer": "Martelo",
    "hunting-horn": "Berrante de Caça",
    "lance": "Lança",
    "gunlance": "Lança-fuzil",
    "switch-axe": "Transmachado",
    "charge-blade": "Lâmina Carregada",
    "insect-glaive": "Glaive Inseto",
    "light-bowgun": "Fuzil Leve",
    "heavy-bowgun": "Fuzil Pesado",
    "bow": "Arco"
}

# Mapeamento de Monstros para Palavras-chave de Armas (Árvores)
MONSTER_TREE_MAP = {
    "legiana": ["legia", "ladra", "glacial", "apsara", "glacia", "hoarcry", "shrieking", "larápia", "larapia", "grita-geada"],
    "velkhana": ["velkhana", "rime", "elussalka", "seraphyd", "frost", "icebrink", "reverente", "friminência", "friminencia"],
    "beotodus": ["beo", "beotodus", "mamute", "mammoth"],
    "barioth": ["barioth", "amber", "frostfang", "adulária", "adularia", "âmbar", "presa", "gume", "caninâmbar", "caninambar"],
    "nargacuga": ["narga", "hidden", "nightshade", "oculto", "negra", "crepúsculo"],
    "tigrex": ["tigrex", "rex", "brute", "molten", "bravo"],
    "rathalos": ["rathalos", "wyvern", "azure", "silver", "prateado", "azul", "fogo", "céu"],
    "rathian": ["rathian", "pink", "gold", "rosa", "dourada", "veneno", "terra"],
    "zinogre": ["zinogre", "usurper", "stygian", "despot", "estígio", "trovão", "usurpador"],
    "glavenus": ["glavenus", "acidic", "acid", "ácido", "espada", "cortante"],
    "brachydios": ["brachy", "dios", "raging", "explosivo", "fúria", "demolidor"],
    "odogaron": ["odogaron", "ebony", "sin", "ebâneo", "sangue", "pecado", "cruel"],
    "anjanath": ["anjan", "fulgur", "flame", "chama", "fulgurante", "brasa"],
    "diablos": ["diablos", "black", "tyrant", "negra", "tirano", "caos"],
    "pukei": ["pukei", "coral", "datura"],
    "kulu": ["kulu", "ya-ku", "dazzle"]
}

def _get_monster_from_name(name_en: str, name_pt: str) -> Optional[str]:
    """Tenta inferir o monstro de origem a partir do nome da arma/armadura."""
    n_en = name_en.lower()
    n_pt = name_pt.lower()
    for monster, keywords in MONSTER_TREE_MAP.items():
        for kw in keywords:
            if kw in n_en or kw in n_pt:
                return monster.capitalize()
    return None

ELEMENT_MAP = {
    "fogo": "Fire", "fire": "Fire",
    "água": "Water", "agua": "Water", "water": "Water",
    "gelo": "Ice", "ice": "Ice",
    "raio": "Thunder", "trovão": "Thunder", "thunder": "Thunder",
    "dragão": "Dragon", "dragao": "Dragon", "dragon": "Dragon",
    "veneno": "Poison", "poison": "Poison",
    "paralisia": "Paralysis", "paralysis": "Paralysis",
    "sono": "Sleep", "sleep": "Sleep",
    "explosão": "Blast", "explosao": "Blast", "blast": "Blast"
}

SKILL_MAP = {
    # Elementos
    "ataque de fogo": "Fire Attack", "fogo": "Fire Attack", "fire attack": "Fire Attack",
    "resistência a fogo": "Fire Resistance", "resistencia a fogo": "Fire Resistance", "fire resistance": "Fire Resistance",
    "ataque de água": "Water Attack", "água": "Water Attack", "agua": "Water Attack", "water attack": "Water Attack",
    "resistência a água": "Water Resistance", "resistencia a agua": "Water Resistance", "water resistance": "Water Resistance",
    "ataque de gelo": "Ice Attack", "gelo": "Ice Attack", "ice attack": "Ice Attack",
    "resistência a gelo": "Ice Resistance", "resistencia a gelo": "Ice Resistance", "ice resistance": "Ice Resistance",
    "ataque de raio": "Thunder Attack", "raio": "Thunder Attack", "thunder attack": "Thunder Attack",
    "resistência a raio": "Thunder Resistance", "resistencia a raio": "Thunder Resistance", "thunder resistance": "Thunder Resistance",
    "ataque de dragão": "Dragon Attack", "dragão": "Dragon Attack", "dragon attack": "Dragon Attack",
    "resistência a dragão": "Dragon Resistance", "resistencia a dragao": "Dragon Resistance", "dragon resistance": "Dragon Resistance",
    # Ataque e Crítico
    "reforço de ataque": "Attack Boost", "ataque": "Attack Boost", "attack boost": "Attack Boost",
    "olho crítico": "Critical Eye", "olho critico": "Critical Eye", "critical eye": "Critical Eye", "afinidade": "Critical Eye",
    "exploração de fraqueza": "Weakness Exploit", "ponto fraco": "Weakness Exploit", "weakness exploit": "Weakness Exploit",
    "bônus crítico": "Critical Boost", "reforço crítico": "Critical Boost", "reforco critico": "Critical Boost", "critical boost": "Critical Boost",
    "agitador": "Agitator", "desafiante": "Agitator", "agitator": "Agitator",
    "poder máximo": "Maximum Might", "maximum might": "Maximum Might",
    "desempenho máximo": "Peak Performance", "peak performance": "Peak Performance",
    "indignação": "Resentment", "resentment": "Resentment",
    "poder latente": "Latent Power", "latent power": "Latent Power",
    # Sobrevivência e Utilidade
    "reforço de vida": "Health Boost", "vida": "Health Boost", "health boost": "Health Boost",
    "bênção divina": "Divine Blessing", "bencao divina": "Divine Blessing", "divine blessing": "Divine Blessing",
    "tampões": "Earplugs", "tampão de ouvidos": "Earplugs", "earplugs": "Earplugs",
    "manutenção": "Tool Specialist", "especialista em ferramentas": "Tool Specialist", "tool specialist": "Tool Specialist",
    "quebra-partes": "Partbreaker", "destruidor": "Partbreaker", "partbreaker": "Partbreaker",
    "fortificar": "Fortify", "fortify": "Fortify",
    # Movimentação e Stamina
    "constituição": "Constitution", "constitution": "Constitution",
    "pico de stamina": "Stamina Surge", "stamina surge": "Stamina Surge",
    "corrida": "Marathon Runner", "marathon runner": "Marathon Runner",
    "extensor de esquiva": "Evade Extender", "evade extender": "Evade Extender",
    "janela de esquiva": "Evade Window", "evade window": "Evade Window",
    # Armas Específicas
    "artesanato": "Handicraft", "handicraft": "Handicraft",
    "foco": "Focus", "focus": "Focus",
    "bloqueio": "Guard", "guard": "Guard",
    "bloqueio ofensivo": "Offensive Guard", "offensive guard": "Offensive Guard",
    "artilharia": "Artillery", "artillery": "Artillery",
    "comer rápido": "Speed Eating", "speed eating": "Speed Eating",
    "refeição grátis": "Free Meal", "free meal": "Free Meal",
    "ampla gama": "Wide-Range", "wide-range": "Wide-Range"
}

MONSTER_EQUIPMENT_MAP = {
    "legiana": "Legiana",
    "shrieking legiana": "Legiana",
    "velkhana": "Rimeguard",
    "teostra": "Kaiser",
    "kushala": "Kushala",
    "lunastra": "Empress",
    "vaal hazak": "Vaal Hazak", 
    "blackveil vaal hazak": "Vaal Hazak",
    "namielle": "Tentacle",
    "shara ishvalda": "Shara",
    "zinogre": "Zinogre",
    "stygian zinogre": "Stygian",
    "rajang": "Golden",
    "furious rajang": "Grand God",
    "safi'jiiva": "Safi",
    "kulve taroth": "Kjarr", # Mudado para Kjarr/Taroth por ser mais comum
    "alatreon": "Escadora",
    "fatalis": "Dragon",
    "kirin": "Kirin",
    "nergigante": "Nergigante",
    "ruiner nergigante": "Ruiner",
    "anjanath": "Anja",
    "glavenus": "Glavenus",
    "acidic glavenus": "Acidic Glavenus",
    "barioth": "Barioth",
    "tigrex": "Tigrex",
    "brachydios": "Brachydios",
    "raging brachydios": "Brachydium",
    "garuga": "Garuga",
    "yian garuga": "Garuga",
    "scarred yian garuga": "Garuga",
    "rimeguard": "Rimeguard"
}

# === Jewel Substitution Map (RNG Friendly) ===
JEWEL_SUBSTITUTION_MAP = {
    "Attack Jewel+ 4": {
        "rarity": 12, "points": 2, "skill": "Attack Boost",
        "subs": ["Attack Jewel 1", "Ironwall/Attack Jewel 4", "Crisis/Attack Jewel 4"]
    },
    "Expert Jewel+ 4": {
        "rarity": 12, "points": 2, "skill": "Critical Eye",
        "subs": ["Expert Jewel 1", "Maintenance/Expert Jewel 4", "Tool Specialist/Expert Jewel 4"]
    },
    "Challenger Jewel+ 4": {
        "rarity": 12, "points": 2, "skill": "Agitator",
        "subs": ["Challenger Jewel 2", "Challenger/Maintenance Jewel 4", "Challenger/Vitality Jewel 4"]
    },
    "Critical/Vitality Jewel 4": {
        "rarity": 11, "points": 1, "skill": "Critical Boost",
        "subs": ["Critical Jewel 2", "Critical/Protection Jewel 4"]
    },
    "Tenderizer/Vitality Jewel 4": {
        "rarity": 11, "points": 1, "skill": "Weakness Exploit",
        "subs": ["Tenderizer Jewel 2", "Tenderizer/Protection Jewel 4"]
    },
    "Handicraft Jewel+ 4": {
        "rarity": 12, "points": 2, "skill": "Handicraft",
        "subs": ["Handicraft Jewel 3", "Handicraft/Maintenance Jewel 4"]
    },
    "Release/Vitality Jewel 4": {
        "rarity": 11, "points": 1, "skill": "Free Elem/Ammo Up",
        "subs": ["Release Jewel 3", "Release/Protection Jewel 4"]
    }
}

# === Core Functions ===

def search_equipment(
    query_name: Optional[str] = None,
    skills: Optional[List[str]] = None,
    rank: Optional[str] = None,
    piece_type: Optional[str] = None,
    min_slots: Optional[int] = None,
    element: Optional[str] = None,
    max_rarity: Optional[int] = None,
    category: str = "armor"
) -> str:
    """
    Busca equipamentos (armaduras ou armas) no banco de dados verificado da Wiki.
    """
    conn = sqlite3.connect(MHW_DB_PATH)
    cursor = conn.cursor()

    # Normalize Weapon Type
    if piece_type and piece_type.lower() in WEAPON_MAP:
        piece_type = WEAPON_MAP[piece_type.lower()]

    # Normalize Element
    if element and element.lower() in ELEMENT_MAP:
        element = ELEMENT_MAP[element.lower()]

    # Normalize Skills
    if skills:
        normalized_skills = []
        for s in skills:
            if not s: continue
            s_lower = str(s).lower().strip()
            if s_lower in SKILL_MAP:
                normalized_skills.append(SKILL_MAP[s_lower])
            else:
                # Fuzzy Match
                best_match = None
                max_len = 0
                for k, v in SKILL_MAP.items():
                    if k in s_lower and len(k) > max_len:
                        best_match = v
                        max_len = len(k)
                if best_match:
                    normalized_skills.append(str(best_match))
                else:
                    normalized_skills.append(str(s))
        skills = normalized_skills

    # Detecção automática de Rank via Perfil (se não especificado)
    if not rank:
        try:
            from data.db import get_user_config
            user_mr = get_user_config("mr", 1)
            rank = "MR" if user_mr > 0 else "HR/LR"
        except:
            rank = "MR"

    results = []
    params: List[Any] = []
    where_clauses = []

    # Filter by Name (Monster or Set)
    name_filters = []
    if query_name:
        name_filters.append(f"%{query_name}%")
        q_lower = query_name.lower()
        if q_lower in MONSTER_EQUIPMENT_MAP:
            name_filters.append(f"%{MONSTER_EQUIPMENT_MAP[q_lower]}%")

    if category == "armor":
        sql = """
            SELECT DISTINCT a.id, a.name, a.type, a.rank, a.rarity, a.defense_base, a.defense_max,
                            a.slot_1, a.slot_2, a.slot_3
            FROM wiki_armor a
        """
        if skills:
            sql += " JOIN wiki_armor_skills was ON a.id = was.armor_id"
            skill_placeholders = ",".join(["?"] * len(skills))
            where_clauses.append(f"(was.skill_name IN ({skill_placeholders}))")
            params.extend(skills)

        if name_filters:
            or_clause = " OR ".join(["a.name LIKE ?" for _ in name_filters])
            where_clauses.append(f"({or_clause})")
            params.extend(name_filters)

        if rank:
            where_clauses.append("a.rank = ?")
            params.append(rank)
        
        if piece_type:
            where_clauses.append("a.type = ?")
            params.append(piece_type)

        if min_slots:
            where_clauses.append("(a.slot_1 >= ? OR a.slot_2 >= ? OR a.slot_3 >= ?)")
            params.extend([min_slots, min_slots, min_slots])

        if max_rarity:
            where_clauses.append("a.rarity <= ?")
            params.append(max_rarity)

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        
        sql += " ORDER BY a.rarity DESC, a.defense_max DESC LIMIT 15"

        try:
            # Source Guessing
            cursor.execute("SELECT name FROM monster_text WHERE lang_id='en'")
            monster_names = {r[0] for r in cursor.fetchall()}

            for row in cursor.execute(sql, params):
                armor_id = row[0]
                skills_query = """
                    SELECT was.skill_name, st.name as name_pt, was.level
                    FROM wiki_armor_skills was
                    LEFT JOIN skilltree_text st ON was.skill_id = st.id AND st.lang_id = 'pt'
                    WHERE was.armor_id = ?
                """
                piece_skills = conn.execute(skills_query, (armor_id,)).fetchall()
                
                source_monster = None
                for mn in monster_names:
                    if mn in row[1]:
                        source_monster = mn
                        break

                results.append({
                    "name": row[1],
                    "type": row[2],
                    "rank": row[3],
                    "rarity": row[4],
                    "defense": f"{row[5]}-{row[6]}",
                    "slots": [s for s in [row[7], row[8], row[9]] if s > 0],
                    "skills": [
                        {"name_en": s[0], "name_pt": s[1] or s[0], "level": s[2]} 
                        for s in piece_skills
                    ],
                    "suspected_source": source_monster
                })
        except Exception as e:
            conn.close()
            return f"Erro na busca de armadura: {str(e)}"

    else: # category == "weapon"
        sql = """
            SELECT w.id, wt_en.name as name_en, wt_pt.name as name_pt, 
                   w.weapon_type, w.rarity, w.attack, w.affinity, 
                   w.element1, w.element1_attack, w.slot_1, w.slot_2, w.slot_3,
                   w.element_hidden
            FROM weapon w
            JOIN weapon_text wt_en ON w.id = wt_en.id AND wt_en.lang_id = 'en'
            LEFT JOIN weapon_text wt_pt ON w.id = wt_pt.id AND wt_pt.lang_id = 'pt'
            WHERE (1=1)
        """
        
        if name_filters:
            # Busca em EN e PT
            or_clauses = []
            final_name_filters = []
            
            for nf in name_filters:
                # Remove os % para checar a chave pura
                clean_name = nf.replace("%", "").lower()
                
                # Smart Monster Search: Se for um monstro conhecido, expande a busca
                if clean_name in MONSTER_TREE_MAP:
                    keywords = MONSTER_TREE_MAP[clean_name]
                    for kw in keywords:
                        or_clauses.append("wt_en.name LIKE ?")
                        or_clauses.append("wt_pt.name LIKE ?")
                        final_name_filters.extend([f"%{kw}%", f"%{kw}%"])
                
                # Sempre inclui o termo original
                or_clauses.append("wt_en.name LIKE ?")
                or_clauses.append("wt_pt.name LIKE ?")
                final_name_filters.extend([nf, nf])
            
            where_clauses.append(f"({' OR '.join(or_clauses)})")
            params.extend(final_name_filters)
        
        if rank:
            if rank == "MR":
                where_clauses.append("w.rarity >= 9")
            else:
                where_clauses.append("w.rarity < 9")
            
        if piece_type: 
            db_type = piece_type.lower().replace(" ", "-")
            where_clauses.append("w.weapon_type = ?")
            params.append(db_type)
            
        if element:
            where_clauses.append("(w.element1 = ? OR w.element2 = ?)")
            params.extend([element, element])

        if max_rarity:
            where_clauses.append("w.rarity <= ?")
            params.append(max_rarity)

        if where_clauses:
            sql += " AND " + " AND ".join(where_clauses)
        
        sql += " ORDER BY w.rarity DESC, w.attack DESC LIMIT 15"

        try:
            for row in cursor.execute(sql, params):
                elem_str = f"{row[7]} {row[8]}" if row[7] else "None"
                if row[12] == 1: # hidden
                    elem_str += " (Hidden)"
                
                w_type = row[3]
                type_pt = TYPE_PT_MAP.get(w_type, w_type)
                    
                results.append({
                    "id": row[0],
                    "name_en": row[1],
                    "name_pt": row[2] or row[1],
                    "type_en": w_type,
                    "type_pt": type_pt,
                    "rarity": row[4],
                    "attack": row[5],
                    "affinity": f"{row[6]}%" if row[6] is not None else "0%",
                    "element": elem_str,
                    "slots": [s for s in [row[9], row[10], row[11]] if s > 0],
                    "monstro": _get_monster_from_name(row[1], row[2] or row[1])
                })
        except Exception as e:
            conn.close()
            return f"Erro na busca de armas: {str(e)}"

    conn.close()
    if not results:
        return "Nenhum equipamento encontrado com esses critérios."
    return json.dumps(results, indent=2, ensure_ascii=False)


def get_armor_details(armor_name: str) -> Optional[dict]:
    """Busca detalhes técnicos de uma armadura de forma flexível (PT/EN/Variações)."""
    conn = sqlite3.connect(MHW_DB_PATH)
    cursor = conn.cursor()
    
    # 1. Normalização do termo de busca
    search_name = armor_name.lower().strip()
    # Mapeamentos comuns para símbolos gregos e Iceborne
    replacements = {
        "alpha": "α", "beta": "β", "gamma": "γ",
        " a+": " α+", " b+": " β+", " g+": " γ+",
        " a ": " α ", " b ": " β ",
        "a+": "α+", "b+": "β+", "g+": "γ+"
    }
    for k, v in replacements.items():
        if k in search_name:
            search_name = search_name.replace(k, v)
    
    # Lista de variantes para tentar busca exata
    variants = [search_name]
    # Substituições de monstros (Anjanath -> Anja, etc)
    for full, short in MONSTER_EQUIPMENT_MAP.items():
        if full in search_name:
            variants.append(search_name.replace(full, short))
        if short.lower() in search_name and short.lower() != full:
            variants.append(search_name.replace(short.lower(), full))
            
    # Tenta encontrar o ID no armor_text (PT ou EN)
    placeholders = ",".join(["?"] * len(variants))
    sql_find_id = f"""
        SELECT id FROM armor_text 
        WHERE (name IN ({placeholders}) OR name LIKE ?) 
        AND lang_id IN ('pt', 'en')
        LIMIT 1
    """
    params = variants + [f"%{search_name}%"]
    cursor.execute(sql_find_id, params)
    row_id = cursor.fetchone()
    
    found_id = row_id[0] if row_id else None
    
    # 2. Busca na wiki_armor (onde estão os slots de Iceborne)
    # Tenta por Nome da Wiki (Inglês) ou por Nome PT
    wiki_sql = """
        SELECT wa.id, wa.name, wa.slot_1, wa.slot_2, wa.slot_3, a.armorset_id
        FROM wiki_armor wa
        LEFT JOIN armor_text at ON wa.id = at.id -- Tentativa de link por ID
        LEFT JOIN armor a ON (wa.id = a.id OR at.id = a.id)
        WHERE (wa.name IN ({vars}) OR wa.name LIKE ?)
        OR (at.name IN ({vars}) OR at.name LIKE ?)
        ORDER BY CASE WHEN wa.name LIKE ? THEN 0 ELSE 1 END
        LIMIT 1
    """.replace('{vars}', placeholders)
    
    wiki_params = variants + [f"%{search_name}%"] + variants + [f"%{search_name}%"] + [f"%{search_name}%"]
    cursor.execute(wiki_sql, wiki_params)
    wiki_row = cursor.fetchone()
    
    if not wiki_row:
        # Se não achou na Wiki, tenta na tabela Armor padrão (fallback)
        if found_id:
            cursor.execute("SELECT id, slot_1, slot_2, slot_3, armorset_id FROM armor WHERE id = ?", (found_id,))
            std_row = cursor.fetchone()
            if std_row:
                # Ajuste de nomes se veio da tabela padrão
                cursor.execute("SELECT name FROM armor_text WHERE id = ? AND lang_id = 'pt'", (found_id,))
                pt_name_row = cursor.fetchone()
                name = pt_name_row[0] if pt_name_row else f"Armor #{found_id}"
                # Formato esperado: (id, name, slot_1, slot_2, slot_3, armorset_id)
                wiki_row = (std_row[0], name, std_row[1], std_row[2], std_row[3], std_row[4])
        
    if not wiki_row:
        conn.close()
        return None
        
    armor_id, name, s1, s2, s3, set_id = wiki_row
    
    # 3. Skills (Prioriza tabela wiki_armor_skills se disponível, senão armor_skill)
    cursor.execute("SELECT COUNT(*) FROM wiki_armor_skills WHERE armor_id = ?", (armor_id,))
    has_wiki_skills = cursor.fetchone()[0] > 0
    
    if has_wiki_skills:
        cursor.execute("""
            SELECT was.skill_name, was.level, st.max_level
            FROM wiki_armor_skills was
            JOIN skilltree st ON was.skill_id = st.id
            WHERE was.armor_id = ?
        """, (armor_id,))
    else:
        cursor.execute("""
            SELECT stt.name, ars.level, st.max_level
            FROM armor_skill ars
            JOIN skilltree st ON ars.skilltree_id = st.id
            JOIN skilltree_text stt ON st.id = stt.id AND stt.lang_id = 'pt'
            WHERE ars.armor_id = ?
        """, (armor_id,))
        
    skills = [{"name": r[0], "points": r[1], "max": r[2]} for r in cursor.fetchall()]
    
    # 4. Set Bonus
    set_bonus = None
    if set_id:
        cursor.execute("SELECT name FROM armorset_text WHERE id = ? AND lang_id = 'pt'", (set_id,))
        set_name_row = cursor.fetchone()
        if not set_name_row:
            cursor.execute("SELECT name FROM armorset_text WHERE id = ? AND lang_id = 'en'", (set_id,))
            set_name_row = cursor.fetchone()
        if set_name_row:
            set_bonus = {"id": set_id, "name": set_name_row[0]}
            
    conn.close()
    return {
        "name": name,
        "slots": [s for s in [s1, s2, s3] if s > 0],
        "skills": skills,
        "set_bonus": set_bonus
    }


def get_weapon_details(weapon_name: str) -> Optional[dict]:
    """Busca detalhes técnicos completos de uma arma."""
    conn = sqlite3.connect(MHW_DB_PATH)
    cursor = conn.cursor()
    
    # 1. Normalização e variantes
    search = weapon_name.lower().strip()
    variants = [search, f"%{search}%"]
    
    # Adiciona mapeamento de monstros (ex: "Velkhana" -> "Rimeguard" ou nomes específicos)
    # Mas aqui vamos usar busca por nome no banco que é mais direta
    
    # 2. Busca JOIN de weapon + weapon_text
    sql = """
        SELECT w.id, wt_en.name as name_en, wt_pt.name as name_pt, 
               w.weapon_type, w.rarity, w.attack, w.affinity, 
               w.element1, w.element1_attack, w.slot_1, w.slot_2, w.slot_3,
               w.element_hidden
        FROM weapon w
        JOIN weapon_text wt_en ON w.id = wt_en.id AND wt_en.lang_id = 'en'
        LEFT JOIN weapon_text wt_pt ON w.id = wt_pt.id AND wt_pt.lang_id = 'pt'
        WHERE (wt_en.name LIKE ? OR wt_en.name = ? OR wt_pt.name LIKE ? OR wt_pt.name = ?)
        ORDER BY w.rarity DESC, CASE WHEN wt_pt.name LIKE ? THEN 0 ELSE 1 END
        LIMIT 1
    """
    cursor.execute(sql, (f"%{search}%", search, f"%{search}%", search, f"%{search}%"))
    row = cursor.fetchone()
    
    if not row:
        # Tenta na wiki_weapon como fallback
        cursor.execute("SELECT id, name, type, rarity, attack, affinity, element, slot_1, slot_2, slot_3 FROM wiki_weapon WHERE name LIKE ? LIMIT 1", (f"%{search}%",))
        wiki_row = cursor.fetchone()
        if wiki_row:
            w_type = wiki_row[2].lower().replace(" ", "-")
            conn.close()
            return {
                "name_en": wiki_row[1],
                "name_pt": wiki_row[1],
                "type_en": w_type,
                "type_pt": TYPE_PT_MAP.get(w_type, w_type),
                "rarity": wiki_row[3],
                "attack": wiki_row[4],
                "affinity": wiki_row[5],
                "element": wiki_row[6],
                "slots": [s for s in [wiki_row[7], wiki_row[8], wiki_row[9]] if s > 0],
                "monstro": _get_monster_from_name(wiki_row[1], wiki_row[1])
            }
        
    if not row:
        conn.close()
        return None
        
    elem_str = f"{row[7]} {row[8]}" if row[7] else "None"
    if row[12] == 1: # hidden
        elem_str += " (Hidden)"

    w_type = row[3]
    res = {
        "name_en": row[1],
        "name_pt": row[2] or row[1],
        "type_en": w_type,
        "type_pt": TYPE_PT_MAP.get(w_type, w_type),
        "rarity": row[4],
        "attack": row[5],
        "affinity": f"{row[6]}%" if row[6] is not None else "0%",
        "element": elem_str,
        "slots": [s for s in [row[9], row[10], row[11]] if s > 0],
        "monstro": _get_monster_from_name(row[1], row[2] or row[1])
    }
    
    conn.close()
    return res


def get_charm_details(charm_name: str) -> Optional[dict]:
    """Busca detalhes de um amuleto."""
    conn = sqlite3.connect(MHW_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM charm_text WHERE name = ? AND lang_id = 'en'", (charm_name,))
    row = cursor.fetchone()
    if not row:
        # Tenta busca parcial se exato falhar
        cursor.execute("SELECT id, name FROM charm_text WHERE name LIKE ? AND lang_id IN ('pt', 'en') LIMIT 1", (f"%{charm_name}%",))
        row = cursor.fetchone()
        
    if not row:
        conn.close()
        return None
        
    charm_id = row[0]
    # Tenta buscar skills em PT, fallback EN
    cursor.execute("""
        SELECT st.name, cs.level, s.max_level
        FROM charm_skill cs
        JOIN skilltree s ON cs.skilltree_id = s.id
        JOIN skilltree_text st ON s.id = st.id AND st.lang_id = 'pt'
        WHERE cs.charm_id = ?
    """, (charm_id,))
    skills = [{"name": r[0], "points": r[1], "max": r[2]} for r in cursor.fetchall()]

    if not skills:
        cursor.execute("""
            SELECT st.name, cs.level, s.max_level
            FROM charm_skill cs
            JOIN skilltree s ON cs.skilltree_id = s.id
            JOIN skilltree_text st ON s.id = st.id AND st.lang_id = 'en'
            WHERE cs.charm_id = ?
        """, (charm_id,))
        skills = [{"name": r[0], "points": r[1], "max": r[2]} for r in cursor.fetchall()]

    conn.close()
    return {"name": charm_name, "skills": skills}



def validate_build(
    armor_pieces: List[str],
    charm_name: Optional[str] = None,
    weapon_name: Optional[str] = None
) -> str:
    if isinstance(armor_pieces, str):
        try:
            import ast
            parsed = ast.literal_eval(armor_pieces)
            if isinstance(parsed, list):
                armor_pieces = parsed
            else:
                armor_pieces = [armor_pieces]
        except:
            if armor_pieces.startswith("[") and armor_pieces.endswith("]"):
                armor_pieces = [p.strip().strip("'").strip('"') for p in armor_pieces[1:-1].split(",")]
            else:
                armor_pieces = [armor_pieces]

    conn = sqlite3.connect(MHW_DB_PATH)
    cursor = conn.cursor()
    
    all_skills: Dict[str, Dict[str, int]] = {}
    active_sets: Dict[int, Dict[str, Any]] = {}
    total_slots: Dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}
    
    # 1. Processar Armas
    if weapon_name:
        weapon_details = get_weapon_details(weapon_name)
        if weapon_details:
            for slot in weapon_details["slots"]:
                total_slots[slot] += 1

    # 2. Processar Armaduras
    for p_name in armor_pieces:
        details = get_armor_details(p_name)
        if not details: continue
        
        # Somar Skills Innatas
        for s in details["skills"]:
            name = s["name"]
            if name not in all_skills:
                all_skills[name] = {"points": 0, "max": s["max"]}
            all_skills[name]["points"] += s["points"]
            
        # Contar Set Bonus
        if details["set_bonus"]:
            sid = details["set_bonus"]["id"]
            if sid not in active_sets:
                active_sets[sid] = {"name": details["set_bonus"]["name"], "count": 0}
            active_sets[sid]["count"] += 1
            
        # Contar Slots
        for slot in details["slots"]:
            total_slots[slot] += 1
            
    # 3. Processar Amuleto
    if charm_name:
        charm_details = get_charm_details(charm_name)
        if charm_details and "skills" in charm_details:
            for s in charm_details["skills"]:
                name = s.get("name")
                if not name: continue
                if name not in all_skills:
                    all_skills[name] = {"points": 0, "max": s.get("max", 5)}
                all_skills[name]["points"] += s.get("points", 0)
                
    # 4. Lógica de Preenchimento Automático de Joias (BiS Simulation)
    # Definimos joias priorizadas para preenchimento de slots
    bis_jewels = [
        {"name": "Attack Jewel+ 4", "slot": 4, "skill": "Attack Boost", "points": 2},
        {"name": "Expert Jewel+ 4", "slot": 4, "skill": "Critical Eye", "points": 2},
        {"name": "Challenger Jewel+ 4", "slot": 4, "skill": "Agitator", "points": 2},
        {"name": "Critical Jewel 2", "slot": 2, "skill": "Critical Boost", "points": 1},
        {"name": "Tenderizer Jewel 2", "slot": 2, "skill": "Weakness Exploit", "points": 1},
        {"name": "Expert Jewel 1", "slot": 1, "skill": "Critical Eye", "points": 1},
        {"name": "Attack Jewel 1", "slot": 1, "skill": "Attack Boost", "points": 1},
        {"name": "Vitality Jewel 1", "slot": 1, "skill": "Health Boost", "points": 1}
    ]
    
    # Clona slots para manipulação
    available_slots = total_slots.copy()
    jewels_used = []
    
    # 5. Preenchimento de Slots
    # Prioridade: Preencher skills ofensivas até o talo
    for jewel in bis_jewels:
        j_name = str(jewel["name"])
        j_skill = str(jewel["skill"])
        j_slot = int(jewel["slot"])
        j_points = int(jewel["points"])
        
        # Busca no banco o max_level se não tivermos a skill no cache
        if j_skill not in all_skills:
            cursor.execute("SELECT max_level FROM skilltree_text st JOIN skilltree s ON st.id = s.id WHERE st.name = ? AND st.lang_id = 'en'", (j_skill,))
            row = cursor.fetchone()
            if row:
                all_skills[j_skill] = {"points": 0, "max": int(row[0])}
            else:
                continue
                
        # Enquanto houver slot compatível e não exceder o limite da skill
        current_skill = all_skills[j_skill]
        while current_skill["points"] < current_skill["max"]:
            # Tenta encaixar no slot exato ou superior
            filled = False
            for s_lv in range(j_slot, 5):
                if available_slots[s_lv] > 0:
                    available_slots[s_lv] -= 1
                    current_skill["points"] += j_points
                    jewels_used.append(f"{j_name} (Slot Level {s_lv})")
                    filled = True
                    break
            if not filled:
                break

    # 6. Verificar Bônus de Set no DB
    bonuses_triggered = []
    for sid, info in active_sets.items():
        cursor.execute("SELECT armorset_bonus_id FROM armorset WHERE id = ?", (sid,))
        bid_row = cursor.fetchone()
        if bid_row and bid_row[0]:
            bid = bid_row[0]
            cursor.execute("""
                SELECT abs.required, st.name
                FROM armorset_bonus_skill abs
                JOIN skilltree_text st ON abs.skilltree_id = st.id AND st.lang_id = 'en'
                WHERE abs.setbonus_id = ?
            """, (bid,))
            for req, sname in cursor.fetchall():
                if info["count"] >= req:
                    bonuses_triggered.append(f"{info['name']} ({req} peças): {sname}")

    conn.close()
    
    # 7. Formatar Resposta
    report = {
        "status": "Validated",
        "total_skills": [f"{k} Lv{min(v['points'], v['max'])}" for k, v in all_skills.items() if v['points'] > 0],
        "slots_available": total_slots,
        "slots_unused": available_slots,
        "jewels_filled": jewels_used,
        "active_set_bonuses": bonuses_triggered,
        "jewel_notes": "Joias BiS foram auto-preenchidas. Use 'JEWEL_SUBSTITUTION_MAP' para alternativas."
    }
    
    return json.dumps(report, indent=2, ensure_ascii=False)


def get_monster_info(monster_name: str) -> str:
    """busca informações sobre um monstro (fraquezas, hitzones)"""
    conn = sqlite3.connect(MHW_DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, name FROM monster_text WHERE name LIKE ?", (f"%{monster_name}%",))
        monsters = cursor.fetchall()
        if not monsters:
            conn.close()
            return f"Monstro '{monster_name}' não encontrado."
            
        m_id, m_name = monsters[0]
        
        cursor.execute("""
            SELECT weakness_fire, weakness_water, weakness_ice, weakness_thunder, weakness_dragon,
                   weakness_poison, weakness_sleep, weakness_paralysis, weakness_blast, weakness_stun
            FROM monster WHERE id = ?
        """, (m_id,))
        weak_row = cursor.fetchone()
        
        weaknesses = []
        if weak_row:
            labels = ["Fire", "Water", "Ice", "Thunder", "Dragon", "Poison", "Sleep", "Paralysis", "Blast", "Stun"]
            for i, val in enumerate(weak_row):
                if val and val >= 2:
                     weaknesses.append(f"{labels[i]} ({val}*)")

        cursor.execute("""
            SELECT cut, impact, shot, fire, water, ice, thunder, dragon 
            FROM monster_hitzone WHERE monster_id = ?
        """, (m_id,))
        hitzones = cursor.fetchall()
        
        max_ele = {"Fire": 0, "Water": 0, "Ice": 0, "Thunder": 0, "Dragon": 0}
        for hz in hitzones:
            max_ele["Fire"] = max(max_ele["Fire"], hz[3])
            max_ele["Water"] = max(max_ele["Water"], hz[4])
            max_ele["Ice"] = max(max_ele["Ice"], hz[5])
            max_ele["Thunder"] = max(max_ele["Thunder"], hz[6])
            max_ele["Dragon"] = max(max_ele["Dragon"], hz[7])
            
        response = {
            "name": m_name,
            "weaknesses_stars": weaknesses,
            "max_hitzone_values": max_ele,
            "description": "Valores de hitzone acima de 20-25 indicam boa fraqueza elemental. Acima de 45 é ponto fraco (WEX)."
        }
        
        m_lower = m_name.lower()
        equipment_hint = None
        for k, v in MONSTER_EQUIPMENT_MAP.items():
            if k in m_lower:
                equipment_hint = v
                break
        if equipment_hint:
             response["armor_set_name_hint"] = equipment_hint

        conn.close()
        return json.dumps(response, indent=2, ensure_ascii=False)
    except Exception as e:
        conn.close()
        return f"Erro ao buscar monstro: {str(e)}"

MHW_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_equipment",
            "description": "Busca armaduras e armas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["armor", "weapon"], "description": "Category (armor or weapon)."},
                    "query_name": {"type": "string", "description": "Search by name or monster (e.g., 'Teostra', 'Zinogre')."},
                    "skills": {"type": "array", "items": {"type": "string"}, "description": "Filter by specific skills in English (e.g., ['Health Boost'])."},
                    "rank": {"type": "string", "enum": ["MR", "HR/LR"], "description": "Game rank."},
                    "piece_type": {"type": "string", "description": "For armor: Head, Chest, Arms, Waist, Legs. For weapons: Long Sword, Hammer, etc."},
                    "element": {"type": "string", "description": "Element for weapons only."},
                    "min_slots": {"type": "integer", "description": "Min slot level."},
                    "max_rarity": {"type": "integer", "description": "Filter by rarity (1-12)."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_monster_info",
            "description": "Fetch monster datasheet including elemental weaknesses and raw hitzones.",
            "parameters": {
                "type": "object",
                "properties": {
                    "monster_name": {"type": "string", "description": "Name of the monster."}
                },
                "required": ["monster_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "build_validator",
            "description": "Calculates final skills, checks slots and set bonuses for a build. Required for final builds.",
            "parameters": {
                "type": "object",
                "properties": {
                    "armor_pieces": {"type": "array", "items": {"type": "string"}, "description": "List of 5 armor pieces."},
                    "charm_name": {"type": "string", "description": "Name of the charm."},
                    "weapon_name": {"type": "string", "description": "Name of the weapon."}
                },
                "required": ["armor_pieces"]
            }
        }
    }
]
