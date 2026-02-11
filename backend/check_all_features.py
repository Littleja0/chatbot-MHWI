import sqlite3

conn = sqlite3.connect('mhw.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 60)
print("VERIFICANDO FUNCIONALIDADES ESPECÍFICAS")
print("=" * 60)

# 1. Combinação de Itens (crafting básico)
print("\n=== COMBINAÇÃO DE ITENS ===")
c.execute("PRAGMA table_info(item_combination)")
print("Colunas:", [col[1] for col in c.fetchall()])

# 2. Localizações de Itens (coleta)
print("\n=== LOCAIS DE COLETA ===")
c.execute("PRAGMA table_info(location_item)")
print("Colunas:", [col[1] for col in c.fetchall()])

# 3. Níveis de Pesquisa de Monstros
print("\n=== ESTRUTURA MONSTER ===")
c.execute("PRAGMA table_info(monster)")
print("Colunas:", [col[1] for col in c.fetchall()])

# 4. Armorset Bonus
print("\n=== BÔNUS DE SET ===")
c.execute("PRAGMA table_info(armorset_bonus_skill)")
print("Colunas:", [col[1] for col in c.fetchall()])

# 5. Melodias 
print("\n=== MELODIAS HUNTING HORN ===")
c.execute("PRAGMA table_info(weapon_melody)")
print("Colunas:", [col[1] for col in c.fetchall()])

# 6. Itens
print("\n=== ESTRUTURA DE ITENS ===")
c.execute("PRAGMA table_info(item)")
print("Colunas:", [col[1] for col in c.fetchall()])

# RESUMO
print("\n" + "=" * 60)
print("RESUMO DO QUE ESTÁ DISPONÍVEL NO BANCO")
print("=" * 60)

available = [
    ("Monstros (93)", "hitzones, breaks, drops, habitats"),
    ("Armaduras (1595)", "defesa, skills, slots, resistências, set bonus"),
    ("Armas (3544)", "ataque, afinidade, elemento, sharpness, melodias HH"),
    ("Amuletos (317)", "skills, materiais de craft"),
    ("Adornos (404)", "skill, slot size"),
    ("Kinsects (105)", "power, speed, heal, dust effect"),
    ("Skills (178)", "níveis e descrições"),
    ("Itens (1339)", "descrição, categoria, locais de coleta"),
    ("Combinações (101)", "crafting de consumíveis"),
    ("Missões (521)", "monstros, recompensas"),
    ("Ferramentas (20)", "duração, recarga, slots"),
    ("Locais de Coleta (911)", "item, área, percentagem"),
    ("Acampamentos", "por localização"),
]

for item, desc in available:
    print(f"✓ {item}: {desc}")

print("\n" + "=" * 60)
print("NÃO DISPONÍVEL NO BANCO ATUAL")
print("=" * 60)
not_available = [
    "Cantina (receitas, ingredientes, habilidades de comida)",
    "Safari Atacaudas (pesquisa, coleta, caça)",
    "Fundidora Anciã (fundir adornos, alquimia)",
    "Centro de Botanologia (cultivo, fertilizantes)",
    "Argosy (itens materiais/consumíveis)",
    "Vaporizador (combustível, recompensas)",
    "Bestiário (níveis de pesquisa, investigações especiais)",
    "Investigações (mecânicas de investigação)",
]

for item in not_available:
    print(f"✗ {item}")

conn.close()
