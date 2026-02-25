import sqlite3

db_path = r'd:\chatbot MHWI\data\mhw.db'
conn = sqlite3.connect(db_path)

print("--- Samples from armor_text (PT) ---")
cursor = conn.execute("SELECT name FROM armor_text WHERE lang_id = 'pt' LIMIT 50")
for row in cursor.fetchall():
    print(row[0])

print("\n--- Samples from wiki_armor ---")
cursor = conn.execute("SELECT name FROM wiki_armor LIMIT 50")
for row in cursor.fetchall():
    print(row[0])

conn.close()
