import sqlite3

def inspect():
    try:
        conn = sqlite3.connect("mhw.db")
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print("Tables:", tables)
        
        # Helper to print schema
        def print_schema(table):
            print(f"\nSchema for '{table}':")
            cursor.execute(f"PRAGMA table_info({table})")
            for col in cursor.fetchall():
                print(col)
        
        print_schema('monster')
        
        # Check text (localized names)
        if 'monster_text' in tables:
            print_schema('monster_text')
            
        if 'monster_hitzone_text' in tables:
             print_schema('monster_hitzone_text')
        elif 'monster_hitzone' in tables:
             print_schema('monster_hitzone')

        if 'item' in tables:
            print_schema('item')
        if 'item_text' in tables:
            print_schema('item_text')

    except Exception as e:
        print(e)
    finally:
        if 'conn' in locals():
            conn.close()
        
if __name__ == "__main__":
    inspect()
