import sqlite3
import json

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

output = {}

# Find tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]

for table in tables:
    try:
        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
        row = cursor.fetchone()
        if not row: continue
        cols = row.keys()
        
        # Search for Odogaron
        query = f"SELECT * FROM {table} WHERE " + " OR ".join([f"[{col}] LIKE ?" for col in cols])
        cursor.execute(query, ["%Odogaron%"] * len(cols))
        rows = cursor.fetchall()
        
        if rows:
            output[table] = [dict(r) for r in rows]
    except:
        pass

with open("db_search_output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

conn.close()
print("Done")
