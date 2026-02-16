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
    data = pm.read_bytes(weapon_ptr + 0x200, 0x200) # Area do Tipo
    
    print("Dump da area do Tipo (+0x200):")
    for i in range(0, 0x200, 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        abs_off = 0x200 + i
        if val < 5000:
            print(f"  +{hex(abs_off)} (int): {val}")

else:
    print("Nao achou arma.")
