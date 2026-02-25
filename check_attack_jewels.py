import sqlite3
import json

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Find PT-BR attack jewels
cursor.execute("SELECT * FROM decoration_text WHERE lang_id='pt' AND name LIKE '%Ataque%'")
pt_jewels = cursor.fetchall()

results = []
for j in pt_jewels:
    # Find the corresponding decoration info
    cursor.execute("SELECT * FROM decoration WHERE id=?", [j['id']])
    info = cursor.fetchone()
    if info:
        results.append({
            "name": j['name'],
            "slot": info['slot'],
            "skilltree_level": info['skilltree_level'],
            "skilltree2_level": info['skilltree2_level']
        })

conn.close()
with open("attack_jewels_pt.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
