
import sqlite3
import os

DB_PATH = 'mhw.db'

def inspect_starters():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    def get_weapon_stats(name_pattern):
        # normalize name pattern for LIKE
        name_like = f"%{name_pattern}%"
        cursor.execute("""
            SELECT wt.name, w.weapon_type, w.attack, w.attack_true, w.rarity, w.element1, w.element1_attack, w.sharpness
            FROM weapon w
            JOIN weapon_text wt ON w.id = wt.id
            WHERE wt.name LIKE ? AND wt.lang_id = 'pt'
            ORDER BY w.attack_true DESC
        """, (name_like,))
        return cursor.fetchall()

    print("\n--- Ferro I (Iron I) ---")
    data = get_weapon_stats("Ferro I") # Might match "Espada de Ferro I", etc.
    # Actually names are like "Katana de Ferro I", "Lâmina de Ferro I"
    # Better to search by "Key" words or just list some generic ones.
    # Let's try English names as they are more consistent: "Iron ... I"
    
    cursor.execute("""
        SELECT wt.name, w.weapon_type, w.attack, w.attack_true, w.rarity
        FROM weapon w
        JOIN weapon_text wt ON w.id = wt.id
        WHERE wt.lang_id = 'en' AND wt.name LIKE 'Iron% I'
        LIMIT 5
    """)
    for r in cursor.fetchall():
        print(dict(r))

    print("\n--- Osso I (Bone I) ---")
    cursor.execute("""
        SELECT wt.name, w.weapon_type, w.attack, w.attack_true, w.rarity
        FROM weapon w
        JOIN weapon_text wt ON w.id = wt.id
        WHERE wt.lang_id = 'en' AND wt.name LIKE 'Bone% I'
        LIMIT 5
    """)
    for r in cursor.fetchall():
        print(dict(r))

    print("\n--- Defensor I (Defender I) ---")
    # Defender weapons are usually named "Defender ... I" or just "Defender ..."
    cursor.execute("""
        SELECT wt.name, w.weapon_type, w.attack, w.attack_true, w.rarity, w.element1, w.element1_attack
        FROM weapon w
        JOIN weapon_text wt ON w.id = wt.id
        WHERE wt.lang_id = 'en' AND wt.name LIKE 'Defender% I'
        ORDER BY w.attack_true DESC
    """)
    rows = cursor.fetchall()
    for r in rows:
        print(dict(r))

    conn.close()

if __name__ == "__main__":
    inspect_starters()
