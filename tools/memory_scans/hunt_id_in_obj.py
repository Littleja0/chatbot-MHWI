import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

def follow(b_addr, offsets):
    try:
        addr = pm.read_longlong(b_addr)
        for o in offsets[:-1]:
            addr = pm.read_longlong(addr + o)
            if not addr: return 0
        return addr + offsets[-1]
    except: return 0

# Pointer chain para a arma viva
weapon_ptr = follow(base + 0x050139A0, [0x50, 0xC0, 0x8, 0x78])

if weapon_ptr:
    print(f"Weapon Object: {hex(weapon_ptr)}")
    data = pm.read_bytes(weapon_ptr, 0x600) # Ler mais
    
    # Vamos buscar o ID 779, 2103 ou 2738 em QUALQUER lugar do objeto
    targets = {779: "Gigagelo II", 2103: "Sabre Oculto+", 2738: "Fortaleza Cromada I"}
    
    for i in range(0, len(data)-4, 1):
        iv = struct.unpack('<I', data[i:i+4])[0]
        if iv in targets:
            print(f"  🎯 [INT32] {targets[iv]} found at +{hex(i)}")
        hv = struct.unpack('<H', data[i:i+2])[0]
        if hv in targets:
            print(f"  🎯 [INT16] {targets[hv]} found at +{hex(i)}")

else:
    print("Arma nao encontrada.")
