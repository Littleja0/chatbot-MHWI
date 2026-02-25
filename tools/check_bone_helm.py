import sqlite3
import pandas as pd

def check_bone_helm():
    conn = sqlite3.connect("data/mhw.db")
    
    query = """
        SELECT a.id, at.name, a.rank, a.rarity, a.slot_1, a.slot_2, a.slot_3
        FROM armor a
        JOIN armor_text at ON a.id = at.id
        WHERE at.name LIKE 'Bone Helm Alpha %' OR at.name LIKE 'Elmo de Osso Alfa %'
    """
    sample = pd.read_sql(query, conn)
    print(sample)
    
    if not sample.empty:
        armor_id = sample.iloc[0]['id']
        skills = pd.read_sql(f"""
            SELECT st.name, s.level
            FROM armor_skill s
            JOIN skilltree_text st ON s.skilltree_id = st.id
            WHERE s.armor_id = {armor_id} AND st.lang_id = 'pt'
        """, conn)
        print("\n--- Skills ---")
        print(skills)
    
    conn.close()

if __name__ == "__main__":
    check_bone_helm()
