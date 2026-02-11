import sqlite3

conn = sqlite3.connect('mhw.db')
c = conn.cursor()

print("=== Idiomas disponíveis para skills ===")
c.execute("SELECT DISTINCT lang_id FROM skilltree_text")
langs = [r[0] for r in c.fetchall()]
print(langs)

print("\n=== Exemplo de skill em PT ===")
c.execute("SELECT name FROM skilltree_text WHERE lang_id='pt' LIMIT 5")
for r in c.fetchall():
    print(r[0])

print("\n=== Buscando 'Critical Eye' em todos idiomas ===")
c.execute("SELECT lang_id, name FROM skilltree_text WHERE name LIKE '%Critical%' OR name LIKE '%Olho%' OR name LIKE '%Crítico%'")
for r in c.fetchall():
    print(f"{r[0]}: {r[1]}")

conn.close()
