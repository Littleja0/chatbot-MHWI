
import sqlite3
import os

DB_PATH = 'mhw.db'

def inspect_katana():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Get Iron Katana I
        print("\n--- Listing Iron Katana I ---")
        cursor.execute("""
            SELECT w.id, wt.name, w.attack, w.affinity, w.element1,
                   w.element1_attack, w.sharpness, w.previous_weapon_id
            FROM weapon w
            JOIN weapon_text wt ON w.id = wt.id
            WHERE wt.name LIKE 'Iron Katana I'
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            print(dict(row))
        else:
            print("Iron Katana I not found in DB.")

        # Check for lowest tier weapons of other types
        print("\n--- Lowest tier 'First' weapons ---")
        # Where previous_weapon_id is NULL (only if present in dataset)
        cursor.execute("""
            SELECT w.id, w.weapon_type, wt.name, w.rarity 
            FROM weapon w
            JOIN weapon_text wt ON w.id = wt.id
            WHERE w.previous_weapon_id IS NULL AND wt.lang_id='en'
            ORDER BY w.weapon_type
            LIMIT 5
        """)
        rows = cursor.fetchall()
        for r in rows:
            print(dict(r))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_katana()
