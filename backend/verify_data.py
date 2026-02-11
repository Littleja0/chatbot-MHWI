
import sqlite3

def verify_velkhana_armor():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    try:
        # Check Velkhana Helm Alpha+ (Rimeguard Helm alpha+)
        print("--- VERIFYING VELKHANA HELM ALPHA+ (MR) ---")
        
        # 1. Base Stats (Defense, Slots)
        query_armor = """
            SELECT a.*, at.name 
            FROM armor a
            JOIN armor_text at ON a.id = at.id
            WHERE at.name = 'Rimeguard Helm alpha+' AND at.lang_id = 'en'
        """
        armor = conn.execute(query_armor).fetchone()
        
        if not armor:
            print("ERROR: Could not find 'Rimeguard Helm alpha+'")
            return

        print(f"Name: {armor['name']}")
        print(f"Rarity: {armor['rarity']} (Expected: 12)")
        print(f"Defense Base: {armor['defense_base']} (Expected: 154)")
        print(f"Slots: [{armor['slot_1']}, {armor['slot_2']}, {armor['slot_3']}] (Expected: [4, 1, 0])")
        
        # 2. Skills
        query_skills = """
            SELECT st.name, ask.level
            FROM armor_skill ask
            JOIN skilltree_text st ON ask.skilltree_id = st.id
            WHERE ask.armor_id = ? AND st.lang_id = 'en'
        """
        skills = conn.execute(query_skills, (armor['id'],)).fetchall()
        print("\nSkills found:")
        for s in skills:
            print(f"- {s['name']} Lv{s['level']}")
            
        print("\nEXPECTED SKILLS:")
        print("- Critical Draw Lv1")
        print("- Divine Blessing Lv2")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_velkhana_armor()
