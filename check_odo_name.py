import sqlite3

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM armor_text WHERE id=572 AND lang_id='pt'")
row = cursor.fetchone()
print("PT Name for ID 572:", row[0] if row else "Not found")

cursor.execute("SELECT name FROM armor_text WHERE id=572 AND lang_id='en'")
row = cursor.fetchone()
print("EN Name for ID 572:", row[0] if row else "Not found")

conn.close()
