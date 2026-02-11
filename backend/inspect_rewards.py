import sqlite3
import os

DB_PATH = "mhw.db"

def inspect_rewards():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Schema for 'monster_reward':")
        cursor.execute("PRAGMA table_info(monster_reward)")
        for col in cursor.fetchall():
            print(col)
            
        print("\nSchema for 'monster_reward_condition_text':")
        cursor.execute("PRAGMA table_info(monster_reward_condition_text)")
        for col in cursor.fetchall():
            print(col)
            
        print("\nSample 'monster_reward':")
        cursor.execute("SELECT * FROM monster_reward LIMIT 3")
        for row in cursor.fetchall():
            print(row)

        print("\nSample 'monster_reward_condition_text':")
        cursor.execute("SELECT * FROM monster_reward_condition_text LIMIT 3")
        for row in cursor.fetchall():
            print(row)
            
        conn.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    inspect_rewards()
