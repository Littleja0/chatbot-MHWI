import sqlite3
import json

def verify_weapons():
    conn = sqlite3.connect("data/mhw.db")
    cursor = conn.cursor()
    
    print("--- Wiki Weapon Schema ---")
    for col in cursor.execute("PRAGMA table_info(wiki_weapon)"):
        print(col)
        
    print("\n--- Total Count ---")
    count = cursor.execute("SELECT count(*) FROM wiki_weapon").fetchone()[0]
    print(f"Total Weapons: {count}")

    print("\n--- Specific Check: Chrome Deathscythe I ---")
    # Tentar achar exatamente
    rows = cursor.execute("SELECT * FROM wiki_weapon WHERE name LIKE '%Chrome Deathscythe I%' LIMIT 1").fetchall()
    if rows:
        print(f"Row: {rows[0]}")
    else:
        print("Not Found!")
        
    print("\n--- Specific Check: Velkhana (Iceborne Flagship) ---")
    rows = cursor.execute("SELECT * FROM wiki_weapon WHERE name LIKE '%Velkhana%' LIMIT 1").fetchall()
    if rows:
        print(f"Row: {rows[0]}")

    conn.close()

if __name__ == "__main__":
    verify_weapons()
