import sqlite3

def search_feystones():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT i.id, t.name FROM item i JOIN item_text t ON i.id = t.id WHERE t.name LIKE '%Feystone%' OR t.name LIKE '%Pedra de Feitiço%' AND t.lang_id IN ('en', 'pt')")
    print("--- Feystones found ---")
    for row in cursor:
        print(f"ID: {row['id']} | Name: {row['name']}")
    conn.close()

if __name__ == "__main__":
    search_feystones()
