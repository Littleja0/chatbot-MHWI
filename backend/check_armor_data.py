import sqlite3

conn = sqlite3.connect('mhw.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 70)
print("ARMADURAS DO KULU-YA-KU NO BANCO DE DADOS")
print("=" * 70)

# Buscar armaduras Kulu
c.execute("""
    SELECT a.id, a.rarity, a.rank, a.armor_type, 
           at.name, at.lang_id,
           a.defense_base, a.defense_max, a.defense_augment_max,
           a.fire, a.water, a.thunder, a.ice, a.dragon
    FROM armor a
    JOIN armor_text at ON a.id = at.id
    WHERE at.name LIKE '%Kulu%'
    ORDER BY at.lang_id, a.armor_type
""")

rows = c.fetchall()
print(f"\nEncontrados {len(rows)} registros de armadura Kulu:\n")

current_lang = None
for row in rows:
    if row['lang_id'] != current_lang:
        current_lang = row['lang_id']
        print(f"\n--- Idioma: {current_lang.upper()} ---")
    
    print(f"  [{row['armor_type']:6}] {row['name']}")
    print(f"          Rank: {row['rank']}, Raridade: {row['rarity']}")
    print(f"          Defesa: {row['defense_base']}-{row['defense_max']} (Aug: {row['defense_augment_max']})")
    print(f"          Elem: Fogo {row['fire']}, Água {row['water']}, Trovão {row['thunder']}, Gelo {row['ice']}, Dragão {row['dragon']}")

# Verificar skills das armaduras
print("\n" + "=" * 70)
print("SKILLS DAS ARMADURAS KULU")
print("=" * 70)

c.execute("""
    SELECT at.name as armor_name, st.name as skill_name, ars.level
    FROM armor a
    JOIN armor_text at ON a.id = at.id
    JOIN armor_skill ars ON a.id = ars.armor_id
    JOIN skilltree_text st ON ars.skilltree_id = st.id
    WHERE at.name LIKE '%Kulu%' 
      AND at.lang_id = 'en'
      AND st.lang_id = 'en'
    ORDER BY at.name
""")

skills = c.fetchall()
if skills:
    print(f"\nSkills encontradas:")
    for s in skills:
        print(f"  {s['armor_name']}: {s['skill_name']} Lv{s['level']}")
else:
    print("\nNenhuma skill encontrada para armaduras Kulu")
    # Verificar se a tabela armor_skill existe
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='armor_skill'")
    if c.fetchone():
        print("  (tabela armor_skill existe)")
        c.execute("SELECT COUNT(*) FROM armor_skill")
        print(f"  ({c.fetchone()[0]} registros na tabela)")

# Verificar slots
print("\n" + "=" * 70)
print("SLOTS DAS ARMADURAS KULU")
print("=" * 70)

c.execute("""
    SELECT at.name, a.slot_1, a.slot_2, a.slot_3
    FROM armor a
    JOIN armor_text at ON a.id = at.id
    WHERE at.name LIKE '%Kulu%' AND at.lang_id = 'en'
""")

for row in c.fetchall():
    slots = []
    if row['slot_1']: slots.append(f"Slot {row['slot_1']}")
    if row['slot_2']: slots.append(f"Slot {row['slot_2']}")
    if row['slot_3']: slots.append(f"Slot {row['slot_3']}")
    print(f"  {row['name']}: {', '.join(slots) if slots else 'Sem slots'}")

conn.close()
