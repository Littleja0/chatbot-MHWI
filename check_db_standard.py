import sqlite3

db_path = r'd:\chatbot MHWI\data\mhw.db'
conn = sqlite3.connect(db_path)

print("--- Standard armor table (Anjanath MR) ---")
# Buscando ID do Anjanath Helm MR
cursor = conn.execute("SELECT id, name FROM armor_text WHERE name LIKE '%Anja%Elmo%' AND lang_id = 'pt'")
res = cursor.fetchone()
if res:
    a_id, pt_name = res
    print(f"Found PT: {pt_name} (ID: {a_id})")
    
    # Get stats from standard armor table
    cursor = conn.execute("SELECT slot_1, slot_2, slot_3, defense_base, defense_max FROM armor WHERE id = ?", (a_id,))
    stats = cursor.fetchone()
    print(f"Stats (slots, def): {stats}")
    
    # Get English name
    cursor = conn.execute("SELECT name FROM armor_text WHERE id = ? AND lang_id = 'en'", (a_id,))
    en_name = cursor.fetchone()[0]
    print(f"English name: {en_name}")

    # Get skills
    print("Skills:")
    cursor = conn.execute("""
        SELECT st.name, ars.level 
        FROM armor_skill ars 
        JOIN skilltree_text st ON ars.skilltree_id = st.id 
        WHERE ars.armor_id = ? AND st.lang_id = 'pt'
    """, (a_id,))
    for row in cursor.fetchall():
        print(row)
else:
    print("Anjanath Helm MR not found in standard tables.")

conn.close()
