import sqlite3

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Try to find the armor table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'armor%';")
tables = [t[0] for t in cursor.fetchall()]

for table in tables:
    try:
        cursor.execute(f"PRAGMA table_info({table});")
        cols = [c[1] for c in cursor.fetchall()]
        print(f"\nSearching in table: {table}")
        print(f"Columns: {cols}")
        
        cursor.execute(f"SELECT * FROM {table} WHERE name LIKE '%Odogaron%' AND (name LIKE '%Beta%' OR name LIKE '%B+%')")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except:
        pass

conn.close()
