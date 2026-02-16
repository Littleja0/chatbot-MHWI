import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
obj = 0x2b9517f68 

print(f"Buscando '4' (Martelo) e '2412' (Maça) no objeto {hex(obj)}...")

try:
    data = pm.read_bytes(obj, 0x5000) # Ler um bloco grande
    for i in range(0, len(data)-4):
        val = struct.unpack('<I', data[i:i+4])[0]
        if val == 4:
            print(f"  Candidato a TIPO (4) em +{hex(i)}")
        if val == 2412:
            print(f"  ⭐ ACHADO ID (2412) em +{hex(i)}")
except Exception as e:
    print(f"Erro: {e}")
