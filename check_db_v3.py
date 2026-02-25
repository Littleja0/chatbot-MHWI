import sqlite3

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]

for table in tables:
    cursor.execute(f"PRAGMA table_info({table});")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Let's search for "Odogaron" in any column of any table
    placeholders = " OR ".join([f'"{col}" LIKE ?' for col in columns])
    try:
        cursor.execute(f"SELECT * FROM {table} WHERE {placeholders}", ["%Odogaron%"] * len(columns))
        rows = cursor.fetchall()
        if rows:
            print(f"Table: {table}")
            print(f"Columns: {columns}")
            for row in rows:
                if 'Beta' in str(row) or 'b+' in str(row).lower() or 'coil' in str(row).lower() or 'cintura' in str(row).lower():
                    print(row)
    except:
        pass

conn.close()
