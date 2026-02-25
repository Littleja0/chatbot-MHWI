import sqlite3

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, name FROM armor_text WHERE name LIKE '%Odogaron%' AND name LIKE '%Cintura%' AND lang_id='pt'")
rows = cursor.fetchall()
for row in rows:
    print(f"ID: {row[0]}, Name: {row[1]}")

conn.close()
