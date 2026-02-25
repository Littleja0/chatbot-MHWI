import sqlite3
import os

db_path = r"d:\chatbot MHWI\data\mhw.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in mhw.db:")
    for t in tables:
        print(f" - {t[0]}")
    conn.close()
else:
    print("DB not found")
