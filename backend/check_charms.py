import sqlite3

conn = sqlite3.connect('mhw.db')
c = conn.cursor()

# Buscar amuletos com Desafiante ou Challenger
print("=== Buscando Challenger/Desafiante ===")
c.execute("SELECT DISTINCT name FROM charm_text WHERE name LIKE '%Challenger%' OR name LIKE '%Desafiante%'")
for r in c.fetchall():
    print(r[0])

print("\n=== Todos os amuletos (amostra) ===")
c.execute("SELECT DISTINCT name FROM charm_text WHERE lang_id='en' LIMIT 20")
for r in c.fetchall():
    print(r[0])

print("\n=== Idiomas disponíveis ===")
c.execute("SELECT DISTINCT lang_id FROM charm_text")
for r in c.fetchall():
    print(r[0])

conn.close()
