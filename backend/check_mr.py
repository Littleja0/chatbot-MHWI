
import sqlite3

def check_mr_gear():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    try:
        print("--- RIMEGUARD HELM BETA+ ---")
        cursor = conn.execute("""
            SELECT a.slot_1, a.slot_2, a.slot_3, at.name 
            FROM armor a 
            JOIN armor_text at ON a.id = at.id 
            WHERE at.name = 'Rimeguard Helm β+' AND at.lang_id = 'en'
        """)
        row = cursor.fetchone()
        if row:
            print(f"Name: {row['name']}")
            print(f"Slots: [{row['slot_1']}, {row['slot_2']}, {row['slot_3']}] (Expected: [4, 1] or [4, 4]?)")
            
        print("\n--- MR WEAPON CHECK ---")
        # Search for 'Chrome' weapons (usually MR Ore)
        cursor = conn.execute("""
            SELECT w.attack, w.rarity, wt.name 
            FROM weapon w 
            JOIN weapon_text wt ON w.id = wt.id 
            WHERE wt.name LIKE 'Chrome%' AND wt.lang_id = 'en'
            ORDER BY w.attack DESC
            LIMIT 5
        """)
        rows = cursor.fetchall()
        for r in rows:
            print(f"Weapon: {r['name']} | Attack: {r['attack']} | Rarity: {r['rarity']}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_mr_gear()
