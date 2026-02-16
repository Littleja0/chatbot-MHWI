import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
obj = 0x2b9517f68 

print(f"Buscando ID 2412 em offsets distantes do objeto {hex(obj)}...")

try:
    data = pm.read_bytes(obj, 0x10000) # Ler 64KB
    for i in range(0, len(data)-4, 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        if val == 2412:
            print(f"  ⭐ ACHADO ID 2412 em +{hex(i)}")
        if val == 4 and i % 4 == 0:
            # Checar se ID 2412 está por perto
            next_val = struct.unpack('<I', data[i+4:i+8])[0]
            if next_val == 2412:
                 print(f"  🔥 PAR [4, 2412] (Tipo, ID) ACHADO em +{hex(i)}")
except Exception as e:
    print(f"Erro: {e}")
