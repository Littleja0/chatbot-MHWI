import sqlite3

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM decoration_text WHERE lang_id = 'en' AND name LIKE '%/%' LIMIT 10")
for r in cursor.fetchall():
    print(r[0])

conn.close()
