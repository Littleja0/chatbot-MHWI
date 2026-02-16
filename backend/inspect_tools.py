import sqlite3

def inspect_tools():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM tool LIMIT 5")
    print("--- Tool Table Schema/Content ---")
    for row in cursor:
        print(dict(row))
        
    cursor = conn.execute("SELECT * FROM tool_text WHERE lang_id='pt' LIMIT 5")
    print("\n--- Tool Text Table (PT) ---")
    for row in cursor:
        print(dict(row))
    conn.close()

if __name__ == "__main__":
    inspect_tools()
