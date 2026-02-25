import sqlite3

db_path = r"data/mhw.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print(f"Tables: {tables}")

# Get schema for interesting tables
for table in ['decoration', 'decoration_text', 'skilltree', 'skilltree_text']:
    if table in tables:
        print(f"\nSchema for {table}:")
        cursor.execute(f"PRAGMA table_info({table});")
        for col in cursor.fetchall():
            print(col)

conn.close()
