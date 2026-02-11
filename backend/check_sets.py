import sys
import os
sys.path.append(os.path.dirname(__file__))
import mhw_api
import sqlite3

def check_armorset_names():
    conn = mhw_api.get_db_connection()
    c = conn.cursor()
    
    print("Checking armor sets matching '%Kadachi%'...")
    query = """
        SELECT DISTINCT a.armorset_id, ast.name as set_name, a.rank, at.lang_id
        FROM armor a
        JOIN armor_text at ON a.id = at.id
        LEFT JOIN armorset_text ast ON a.armorset_id = ast.id AND ast.lang_id = at.lang_id
        WHERE at.name LIKE '%Kadachi%' 
          AND at.lang_id = 'pt'
        ORDER BY a.rank, ast.name
    """
    rows = c.execute(query).fetchall()
    
    for r in rows:
        print(f"Set ID: {r['armorset_id']} | Rank: {r['rank']} | Set Name: {r['set_name']}")

    conn.close()

if __name__ == "__main__":
    check_armorset_names()
