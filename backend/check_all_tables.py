import sqlite3

conn = sqlite3.connect('mhw.db')
c = conn.cursor()

print("=" * 60)
print("TODAS AS TABELAS DO BANCO DE DADOS MHW")
print("=" * 60)

c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [t[0] for t in c.fetchall()]

for table in tables:
    c.execute(f"SELECT COUNT(*) FROM [{table}]")
    count = c.fetchone()[0]
    print(f"  {table}: {count} registros")

print(f"\nTotal: {len(tables)} tabelas")

# Verificar tabelas específicas
print("\n" + "=" * 60)
print("VERIFICANDO DADOS ESPECÍFICOS")
print("=" * 60)

# Decorations (Adornos/Jewels)
if 'decoration' in tables:
    print("\n--- ADORNOS (Decorations) ---")
    c.execute("SELECT * FROM decoration LIMIT 3")
    cols = [d[0] for d in c.description]
    print(f"Colunas: {cols}")

# Quests (Missões)
quest_tables = [t for t in tables if 'quest' in t.lower()]
print(f"\n--- MISSÕES (Quest tables): {quest_tables}")

# Charm/Amuleto
charm_tables = [t for t in tables if 'charm' in t.lower()]
print(f"\n--- AMULETOS (Charm tables): {charm_tables}")

# Tools/Mantles
tool_tables = [t for t in tables if 'tool' in t.lower()]
print(f"\n--- MANTOS/FERRAMENTAS (Tool tables): {tool_tables}")

# Palico/Amigato
palico_tables = [t for t in tables if 'palico' in t.lower() or 'kinsect' in t.lower()]
print(f"\n--- AMIGATO/PALICO (tables): {palico_tables}")

conn.close()
