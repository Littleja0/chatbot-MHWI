import sqlite3

def list_random_names():
    conn = sqlite3.connect("data/mhw.db")
    cursor = conn.cursor()
    print("--- 20 Random Weapon Names ---")
    rows = cursor.execute("SELECT name, type, attack FROM wiki_weapon ORDER BY RANDOM() LIMIT 20").fetchall()
    for row in rows:
        print(row)
    conn.close()

if __name__ == "__main__":
    list_random_names()
