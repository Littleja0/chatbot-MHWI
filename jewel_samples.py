import sqlite3
import json

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

output = {}

tables = ['decoration', 'decoration_text']
for table in tables:
    try:
        cursor.execute(f"SELECT * FROM {table} LIMIT 10")
        output[table] = [dict(r) for r in cursor.fetchall()]
    except:
        pass

conn.close()
with open("jewel_samples.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
