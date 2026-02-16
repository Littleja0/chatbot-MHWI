import sqlite3

def revert_waist():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    try:
        cursor = conn.cursor()
        # Revert Cinturão de Legiana α+ (ID 1130) to slot_1 = 2
        cursor.execute("UPDATE armor SET slot_1 = 2 WHERE id = 1130")
        conn.commit()
        print("Updated armor ID 1130 with slot_1 = 2")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    revert_waist()
