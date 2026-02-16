import sqlite3, json, sys

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

conn = sqlite3.connect('backend/mhw.db')
cur = conn.cursor()

cur.execute("SELECT id, name FROM armor_text WHERE name LIKE 'Elmo de Couro%' AND lang_id='pt'")
print(cur.fetchall())
conn.close()
