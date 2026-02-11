
import sqlite3

def check_dragon_armor():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    try:
        print("--- CHECKING FOR 'DRAGON' NAMED ARMOR (FATALIS) ---")
        cursor = conn.execute("""
            SELECT at.name, a.rarity, a.slot_1, a.slot_2, a.slot_3
            FROM armor a
            JOIN armor_text at ON a.id = at.id
            WHERE at.name LIKE 'Dragon%' AND a.rarity = 12 AND at.lang_id = 'en'
        """)
        found = False
        for row in cursor.fetchall():
            found = True
            print(f"Name: {row['name']}")
            print(f"Slots: [{row['slot_1']}, {row['slot_2']}, {row['slot_3']}]")
            
        if not found:
            print("No Rarity 12 armor starting with 'Dragon' found.")

        print("\n--- CHECKING ARCH-TEMPERED VELKHANA (GAMMA) ---")
        cursor = conn.execute("SELECT name FROM armor_text WHERE name LIKE 'Rimeguard%gamma%' AND lang_id='en'")
        found_gamma = cursor.fetchall()
        if found_gamma:
            print(f"Found {len(found_gamma)} Rimeguard Gamma pieces.")
        else:
            print("Rimeguard Gamma (AT Velkhana) NOT found.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_dragon_armor()
