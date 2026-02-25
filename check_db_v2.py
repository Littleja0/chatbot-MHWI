import sqlite3

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]

for table in tables:
    cursor.execute(f"PRAGMA table_info({table});")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Table: {table}, Columns: {columns}")
    
    # Let's search for the armor by name in any table that looks like armor
    if 'armor' in table.lower():
        cursor.execute(f"SELECT * FROM {table} WHERE name LIKE '%Odogaron%' AND name LIKE '%Beta%' AND name LIKE '%Coil%' OR name LIKE '%Cintura%'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Row in {table}: {row}")

conn.close()
