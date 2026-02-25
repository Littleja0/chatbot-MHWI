import sqlite3
import json

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

output = {}

# Search for decorations
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%decoration%' OR name LIKE '%jewel%');")
    tables = [t[0] for t in cursor.fetchall()]
    print("Decoration tables:", tables)
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table} WHERE name LIKE '%Attack%' OR name LIKE '%Ataque%'")
        rows = cursor.fetchall()
        output[table] = [dict(r) for r in rows]
except:
    pass

# Check item table for jewels
try:
    cursor.execute("SELECT * FROM item WHERE name LIKE '%Attack%' OR name LIKE '%Ataque%'")
    rows = cursor.fetchall()
    output['item_search'] = [dict(r) for r in rows]
except:
    pass

with open("jewel_search_output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

conn.close()
