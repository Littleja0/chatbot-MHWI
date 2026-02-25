import sqlite3

db_path = r'd:\chatbot MHWI\data\mhw.db'
conn = sqlite3.connect(db_path)

print("--- Searching Portuguese names for Anjanath ---")
# Buscando nomes de Anjanath em PT
cursor = conn.execute("SELECT id, name FROM armor_text WHERE name LIKE '%Anjanath%' AND lang_id = 'pt' LIMIT 30")
for row in cursor.fetchall():
    print(row)

print("\n--- Searching English names for Anjanath ---")
cursor = conn.execute("SELECT id, name FROM armor_text WHERE name LIKE '%Anjanath%' AND lang_id = 'en' LIMIT 30")
for row in cursor.fetchall():
    print(row)

conn.close()
