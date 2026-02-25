import sqlite3
import json
import re
from pathlib import Path

def populate_db():
    scraped_armor_file = Path("data/scraped_armor.json")
    scraped_weapon_file = Path("data/scraped_weapons.json")
    mapping_file = Path("data/skill_mapping.json")
    
    skill_map = json.loads(mapping_file.read_text(encoding="utf-8")) if mapping_file.exists() else {}

    conn = sqlite3.connect("data/mhw.db")
    cursor = conn.cursor()

    # 1. Reinicializar Tabelas com novo esquema
    print("🛠️ Preparando tabelas wiki_armor e wiki_weapon...")
    cursor.execute("DROP TABLE IF EXISTS wiki_armor_skills")
    cursor.execute("DROP TABLE IF EXISTS wiki_armor")
    cursor.execute("DROP TABLE IF EXISTS wiki_weapon")

    cursor.execute("""
        CREATE TABLE wiki_armor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            rank TEXT,
            rarity INTEGER,
            defense_base INTEGER,
            defense_max INTEGER,
            slot_1 INTEGER DEFAULT 0,
            slot_2 INTEGER DEFAULT 0,
            slot_3 INTEGER DEFAULT 0,
            fire INTEGER DEFAULT 0,
            water INTEGER DEFAULT 0,
            thunder INTEGER DEFAULT 0,
            ice INTEGER DEFAULT 0,
            dragon INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE wiki_armor_skills (
            armor_id INTEGER,
            skill_name TEXT,
            skill_id INTEGER,
            level INTEGER,
            FOREIGN KEY(armor_id) REFERENCES wiki_armor(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE wiki_weapon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            rank TEXT,
            rarity INTEGER,
            attack TEXT,
            affinity TEXT,
            element TEXT,
            slot_1 INTEGER DEFAULT 0,
            slot_2 INTEGER DEFAULT 0,
            slot_3 INTEGER DEFAULT 0
        )
    """)

    # 2. Inserir Armaduras
    if scraped_armor_file.exists():
        armor_data = json.loads(scraped_armor_file.read_text(encoding="utf-8"))
        print(f"📥 Inserindo {len(armor_data)} armaduras...")
        for p in armor_data:
            slots = p.get("slots", [])
            s1 = slots[0] if len(slots) > 0 else 0
            s2 = slots[1] if len(slots) > 1 else 0
            s3 = slots[2] if len(slots) > 2 else 0

            res = p.get("resistances", {})
            def clean_res(val):
                m = re.search(r'(-?\d+)', str(val))
                return int(m.group(1)) if m else 0

            cursor.execute("""
                INSERT INTO wiki_armor (name, type, rank, rarity, defense_base, defense_max, slot_1, slot_2, slot_3, fire, water, thunder, ice, dragon)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["name"], p["type"], p["rank"], p["rarity"],
                p.get("defense_base", 0), p.get("defense_max", 0),
                s1, s2, s3,
                clean_res(res.get("fire", 0)), clean_res(res.get("water", 0)),
                clean_res(res.get("thunder", 0)), clean_res(res.get("ice", 0)),
                clean_res(res.get("dragon", 0))
            ))
            
            armor_id = cursor.lastrowid
            for s in p.get("skills", []):
                s_name = s["name"]
                mapped = skill_map.get(s_name.lower())
                cursor.execute("""
                    INSERT INTO wiki_armor_skills (armor_id, skill_name, skill_id, level)
                    VALUES (?, ?, ?, ?)
                """, (armor_id, s_name, mapped["id"] if mapped else None, s["level"]))

    # 3. Inserir Armas
    if scraped_weapon_file.exists():
        weapon_data = json.loads(scraped_weapon_file.read_text(encoding="utf-8"))
        print(f"📥 Inserindo {len(weapon_data)} armas...")
        for w in weapon_data:
            slots = w.get("slots", [])
            s1 = slots[0] if len(slots) > 0 else 0
            s2 = slots[1] if len(slots) > 1 else 0
            s3 = slots[2] if len(slots) > 2 else 0
            rarity = w.get("rarity", 0)
            # Rank Dinâmico baseado na Raridade
            rank = "MR" if rarity >= 9 else "HR/LR"
            # Se já veio do scraper como MR mas a raridade é baixa, corrigimos.
            # O scraper hardcoded como "MR" na lista de categorias, mas aqui refinamos.
            
            cursor.execute("""
                INSERT INTO wiki_weapon (name, type, rank, rarity, attack, affinity, element, slot_1, slot_2, slot_3)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (w["name"], w["type"], rank, rarity, w["attack"], w["affinity"], w["element"], s1, s2, s3))

    # 4. Criar Índices (Critério de Performance)
    print("⚡ Criando índices...")
    cursor.execute("CREATE INDEX idx_wiki_armor_rank ON wiki_armor(rank)")
    cursor.execute("CREATE INDEX idx_wiki_skill_name ON wiki_armor_skills(skill_name)")
    cursor.execute("CREATE INDEX idx_wiki_skill_id ON wiki_armor_skills(skill_id)")
    cursor.execute("CREATE INDEX idx_wiki_weapon_rank ON wiki_weapon(rank)")

    conn.commit()
    conn.close()
    print("✅ Banco de dados atualizado com sucesso!")

if __name__ == "__main__":
    populate_db()
