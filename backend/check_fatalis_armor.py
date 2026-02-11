
import sqlite3

def check_fatalis_armor():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    try:
        print("--- CHECKING FATALIS ARMOR ---")
        # Fatalis armor is typically Rarity 12
        # Name usually contains 'Fatalis' or 'Dragon' depending on localization, but let's search 'Fatalis'
        
        cursor = conn.execute("""
            SELECT a.*, at.name 
            FROM armor a
            JOIN armor_text at ON a.id = at.id
            WHERE at.name LIKE '%Fatalis%' AND at.lang_id = 'en'
        """)
        
        found = False
        for row in cursor.fetchall():
            found = True
            print(f"Name: {row['name']}")
            print(f"Rarity: {row['rarity']}")
            print(f"Slots: [{row['slot_1']}, {row['slot_2']}, {row['slot_3']}]")
            print("---")
            
        if not found:
            print("Fatalis armor NOT found.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_fatalis_armor()
