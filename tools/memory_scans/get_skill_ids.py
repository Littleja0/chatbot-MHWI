import sqlite3, json, sys

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

conn = sqlite3.connect('backend/mhw.db')
cur = conn.cursor()

targets = ['Paralisia', 'Sangramento', 'Sono', 'Veneno']
results = {}
for t in targets:
    cur.execute("SELECT id, name FROM skilltree_text WHERE name LIKE ? AND lang_id='pt'", ('%' + t + '%',))
    results[t] = cur.fetchall()

print(json.dumps(results, indent=2, ensure_ascii=False))
conn.close()
