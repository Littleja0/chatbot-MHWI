import sqlite3

db_path = r"d:\chatbot MHWI\data\mhw.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Search for Odogaron armor
# We'll try to find the table that might contain armor info, e.g., 'armor' or 'armors'
search_query = "Odogaron"
for table_info in tables:
    table = table_info[0]
    try:
        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
        columns = [description[0] for description in cursor.description]
        
        # Check if any column contains the name
        cursor.execute(f"SELECT * FROM {table} WHERE {' OR '.join([f'[{c}] LIKE ?' for c in columns])}", 
                       tuple([f"%{search_query}%"] * len(columns)))
        results = cursor.fetchall()
        if results:
            print(f"--- Table: {table} ---")
            print("Columns:", columns)
            for row in results:
                print(row)
    except Exception as e:
        # Some tables might not have searchable text columns easily
        pass

conn.close()
