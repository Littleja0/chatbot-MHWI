
import sqlite3
import os

DB_PATH = 'mhw.db'

def list_defenders():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n--- Defender Weapons I ---")
    cursor.execute("""
        SELECT wt.name, w.weapon_type, w.attack, w.attack_true, w.element1, w.element1_attack, w.sharpness
        FROM weapon w
        JOIN weapon_text wt ON w.id = wt.id
        WHERE wt.lang_id = 'en' AND wt.name LIKE 'Defender% I'
        ORDER BY w.attack_true DESC
    """)
    rows = cursor.fetchall()
    
    # Calculate effective raw (approximate) or just list them
    for r in rows:
        print(f"{r['name']} ({r['weapon_type']}): Raw {r['attack_true']}, Element {r['element1']} {r['element1_attack']}")

    conn.close()

if __name__ == "__main__":
    list_defenders()
