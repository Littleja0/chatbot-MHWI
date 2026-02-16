import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll
size = pm.process_base.SizeOfImage

def search_id(target_id, label):
    target_bytes = struct.pack('<I', target_id)
    print(f"Buscando {label} (ID {target_id})...")
    
    data = pm.read_bytes(base, size)
    idx = data.find(target_bytes)
    count = 0
    while idx != -1:
        print(f"  [FOUND] base + {hex(idx)}")
        # Ler contexto
        try:
            nearby = data[idx-16 : idx+16]
            print(f"     Contexto (hex): {nearby.hex(' ')}")
        except: pass
        count += 1
        idx = data.find(target_bytes, idx + 4)
    if count == 0: print("  Nada encontrado.")

# Buscar a Maça (2412) e o Sabre (2103)
search_id(2412, "Maça Palácio")
search_id(2103, "Sabre Oculto+")
search_id(2738, "Fortaleza Cromada")
