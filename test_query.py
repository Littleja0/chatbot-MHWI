import sqlite3
import os

db_path = 'backend/mhw.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

monster_name = 'Rathalos'
print(f"--- Searching for {monster_name} ---")
c.execute("SELECT id, name FROM monster_text WHERE name LIKE ? AND lang_id='pt'", (f"%{monster_name}%",))
monsters = c.fetchall()
for m in monsters:
    print(f"ID: {m['id']} | Name: {m['name']}")
    m_id = m['id']
    
    # Armor for this monster
    # We can join armor with armor_text and check if name contains monster name
    # Or check if there is an armorset linked.
    print(f"  Armor pieces matching '{m['name']}':")
    c.execute("""
        SELECT a.id, at.name, a.armor_type, a.slot_1, a.slot_2, a.slot_3
        FROM armor a
        JOIN armor_text at ON a.id = at.id
        WHERE (at.name LIKE ? OR at.name LIKE ?) AND at.lang_id='pt'
    """, (f"%{m['name']}%", f"%Rathalos%"))
    pieces = c.fetchall()
    for p in pieces:
        print(f"    - {p['name']} ({p['armor_type']}) | Slots: {p['slot_1']}, {p['slot_2']}, {p['slot_3']}")
        
        # Skills for this piece
        c.execute("""
            SELECT st.name, ars.level
            FROM armor_skill ars
            JOIN skilltree_text st ON ars.skilltree_id = st.id
            WHERE ars.armor_id = ? AND st.lang_id='pt'
        """, (p['id'],))
        skills = c.fetchall()
        for s in skills:
            print(f"      Skill: {s['name']} Lv{s['level']}")

conn.close()
