import sqlite3

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM armor_text WHERE name LIKE '%Odogaron%' AND lang_id='pt' LIMIT 20")
rows = cursor.fetchall()
for row in rows:
    print(row[0])

conn.close()
