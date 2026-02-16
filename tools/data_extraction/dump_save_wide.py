import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
# Endereço do struct confirmado pelo Zenny
struct_addr = 0x95c5987c 

print(f"Escanendo Save Struct ({hex(struct_addr)}) por IDs 779, 2103, 2738...")
targets = [779, 2103, 2738, 2412, 2804, 2244, 2490]

try:
    # Vamos ler 128KB (o struct de save tem ~320KB)
    data = pm.read_bytes(struct_addr, 0x20000)
    for i in range(0, len(data)-4, 1):
        v = struct.unpack('<I', data[i:i+4])[0]
        if v in targets:
            print(f"  🎯 ACHADO ID {v} no offset +{hex(i)}")
        # Check for shorts as well
        s = struct.unpack('<H', data[i:i+2])[0]
        if s in targets:
             # Só mostrar shorts que não são parte de ints maiores
             if s == v:
                 print(f"  🎯 ACHADO ID (Short) {s} no offset +{hex(i)}")

    # Também checar o Tipo
    wtype = struct.unpack('<I', data[0x74:0x78])[0]
    print(f"Tipo em +0x74: {wtype}")

except Exception as e:
    print(f"Erro: {e}")
