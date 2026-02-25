import sqlite3
import os

# Caminho relativo ao banco de dados
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "..", "..", "data", "mhw.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def check(t):
    print(f"\n--- {t} ---")
    try:
        cursor.execute(f"PRAGMA table_info({t});")
        print([c[1] for c in cursor.fetchall()])
        cursor.execute(f"SELECT * FROM {t} LIMIT 5;")
        for r in cursor.fetchall(): print(r)
    except: print("Error")

check("decoration_text")

conn.close()
