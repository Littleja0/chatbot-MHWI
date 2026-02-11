
import sqlite3

def check_db_integrity():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    try:
        print("--- WEAPON CHECK ---")
        # Iron Katana I
        cursor = conn.execute("""
            SELECT w.attack, w.rarity, wt.name 
            FROM weapon w 
            JOIN weapon_text wt ON w.id = wt.id 
            WHERE wt.name = 'Iron Katana I' AND wt.lang_id = 'en'
        """)
        row = cursor.fetchone()
        if row:
            print(f"Weapon: {row['name']}")
            print(f"Attack: {row['attack']}")
            print(f"Rarity: {row['rarity']}")
        else:
            print("Iron Katana I not found in EN")

        print("\n--- ARMOR SLOT CHECK ---")
        # Check for Level 4 slots
        cursor = conn.execute("SELECT count(*) FROM armor WHERE slot_1 = 4 OR slot_2 = 4 OR slot_3 = 4")
        count_lv4 = cursor.fetchone()[0]
        print(f"Armor pieces with Level 4 slots: {count_lv4}")
        
        # Check Velkhana Helm again
        cursor = conn.execute("""
            SELECT a.slot_1, a.slot_2, a.slot_3, at.name 
            FROM armor a 
            JOIN armor_text at ON a.id = at.id 
            WHERE at.name = 'Rimeguard Helm α+' AND at.lang_id = 'en'
        """)
        row = cursor.fetchone()
        if row:
            print(f"Armor: {row['name']}")
            print(f"Slots: [{row['slot_1']}, {row['slot_2']}, {row['slot_3']}]")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db_integrity()
