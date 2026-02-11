
import sqlite3
import os

DB_PATH = "mhw.db"

if not os.path.exists(DB_PATH):
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("--- ARMOR STATS ---")
cursor.execute("SELECT count(*) FROM armor")
print(f"Total Armor Pieces: {cursor.fetchone()[0]}")

cursor.execute("SELECT DISTINCT rank FROM armor")
ranks = [r[0] for r in cursor.fetchall()]
print(f"Available Ranks: {ranks}")

print("\n--- WEAPON STATS ---")
cursor.execute("SELECT count(*) FROM weapon")
print(f"Total Weapons: {cursor.fetchone()[0]}")

print("\n--- MONSTER STATS ---")
cursor.execute("SELECT count(*) FROM monster")
print(f"Total Monsters: {cursor.fetchone()[0]}")

print("\n--- ICEBORNE CHECK ---")
# Check for Master Rank (MR) specifically
cursor.execute("SELECT count(*) FROM armor WHERE rank = 'MR'")
mr_armor_count = cursor.fetchone()[0]
print(f"Master Rank (Iceborne) Armor Pieces: {mr_armor_count}")

cursor.execute("SELECT name FROM monster_text WHERE lang_id='en' AND name LIKE '%Velkhana%'")
velkhana = cursor.fetchone()
print(f"Velkhana (Iceborne Flagship) present? {'Yes' if velkhana else 'No'}")

conn.close()
