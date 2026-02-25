import sqlite3
import pandas as pd

def check_mr_names():
    conn = sqlite3.connect("data/mhw.db")
    
    query = """
        SELECT at.name, at.lang_id, a.rank
        FROM armor a
        JOIN armor_text at ON a.id = at.id
        WHERE a.rank = 'MR'
        LIMIT 20
    """
    sample = pd.read_sql(query, conn)
    print(sample)
    
    conn.close()

if __name__ == "__main__":
    check_mr_names()
