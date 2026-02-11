
import sqlite3
import os

DB_PATH = 'mhw.db'

def inspect_best_weapon():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Find base weapons (no previous ID) with highest true raw
        print("\n--- Top 10 Base Weapons by True Raw ---")
        cursor.execute("""
            SELECT w.id, wt.name, w.weapon_type, w.attack, w.attack_true, w.rarity, w.affinity
            FROM weapon w
            JOIN weapon_text wt ON w.id = wt.id
            WHERE (w.previous_weapon_id IS NULL OR w.previous_weapon_id = 0)
              AND wt.lang_id = 'pt'
            ORDER BY w.attack_true DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        for r in rows:
            print(dict(r))

        # Check specifically for "Defender" weapons (Defender is usually "Defensor" in PT, or "Guardian")
        # Defender weapons might not have previous_id IS NULL if they are considered an upgrade path, 
        # but usually they are separate. Let's check by name.
        print("\n--- Defender Weapons (Base) ---")
        cursor.execute("""
            SELECT w.id, wt.name, w.weapon_type, w.attack, w.attack_true, w.rarity, w.previous_weapon_id
            FROM weapon w
            JOIN weapon_text wt ON w.id = wt.id
            WHERE wt.name LIKE '%Defensor%' AND wt.lang_id = 'pt'
            ORDER BY w.attack_true DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        for r in rows:
            print(dict(r))

        # Also generic check for "V" weapons (Defender V) vs "I"
        # Let's just look for "Defensor I"
        print("\n--- Defensor I ---")
        cursor.execute("""
            SELECT w.id, wt.name, w.weapon_type, w.attack, w.attack_true, w.rarity
            FROM weapon w
            JOIN weapon_text wt ON w.id = wt.id
            WHERE wt.name LIKE '%Defensor%I' AND wt.lang_id = 'pt' 
            ORDER BY w.attack_true DESC
        """)
        rows = cursor.fetchall()
        for r in rows:
            print(dict(r))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_best_weapon()
