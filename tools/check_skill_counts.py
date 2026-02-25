import sqlite3

def check_skill_counts():
    conn = sqlite3.connect("data/mhw.db")
    
    print("--- Skill Counts (Top 10) ---")
    query = """
        SELECT skill_name, count(*) as count
        FROM wiki_armor_skills
        GROUP BY skill_name
        ORDER BY count DESC
        LIMIT 10
    """
    for row in conn.execute(query):
        print(f"{row[0]}: {row[1]}")
    
    print("\n--- Health Boost Pieces ---")
    hb_query = """
        SELECT a.name, was.level
        FROM wiki_armor a
        JOIN wiki_armor_skills was ON a.id = was.armor_id
        WHERE was.skill_name = 'Health Boost'
    """
    for row in conn.execute(hb_query):
        print(f"{row[0]} (Lvl {row[1]})")
        
    conn.close()

if __name__ == "__main__":
    check_skill_counts()
