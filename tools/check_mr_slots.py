import sqlite3
import pandas as pd

def check_mr_slots():
    conn = sqlite3.connect("data/mhw.db")
    
    query = """
        SELECT a.id, at.name, a.slot_1, a.slot_2, a.slot_3
        FROM armor a
        JOIN armor_text at ON a.id = at.id
        WHERE at.name = 'Elmo Ósseo α+' AND at.lang_id = 'pt'
    """
    sample = pd.read_sql(query, conn)
    print(sample)
    
    conn.close()

if __name__ == "__main__":
    check_mr_slots()
