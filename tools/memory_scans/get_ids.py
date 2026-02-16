import sqlite3, json, sys

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

conn = sqlite3.connect('backend/mhw.db')
cur = conn.cursor()

targets = [
    ('armor_text', 'Cabelo de Oolong%'),
    ('armor_text', 'Tecido Astral%'),
    ('armor_text', 'Avambraços de Kulu%'),
    ('armor_text', 'Cinturão de Odogaron%'),
    ('armor_text', 'Meias-calças Astral%'),
    ('charm_text', 'Amuleto de Ataque III')
]

results = {}
for table, pattern in targets:
    cur.execute(f"SELECT id, name FROM {table} WHERE name LIKE ? AND lang_id='pt'", (pattern,))
    results[pattern] = cur.fetchall()

print(json.dumps(results, indent=2, ensure_ascii=False))
conn.close()
