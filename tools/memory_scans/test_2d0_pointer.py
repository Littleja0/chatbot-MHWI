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

weapon_obj = follow(base + 0x050139A0, [0x50, 0xC0, 0x8, 0x78])

if weapon_obj:
    print(f"Weapon Object: {hex(weapon_obj)}")
    # O offset 0x2D0 costuma ser um ponteiro para o equipamento ativo (arma)
    equip_ptr = pm.read_longlong(weapon_obj + 0x2D0)
    print(f"Equip Pointer (+0x2D0): {hex(equip_ptr)}")
    
    if equip_ptr:
        # Vamos ler o que tem lá. O ID da arma no MHW costuma estar no offset 0x08 ou 0x0C deste bloco
        data = pm.read_bytes(equip_ptr, 0x100)
        # Scan por 2412 (ID do Martelo) neste bloco
        for i in range(0, 0x40, 4):
            val = struct.unpack('<I', data[i:i+4])[0]
            print(f"  Offset +{hex(i)} (int): {val}")
            if val == 2412:
                print(f"    ⭐ ACHADO ID 2412 em +{hex(i)}!")
    else:
        print("Equip Pointer (+0x2D0) está zerado.")
else:
    print("Arma não encontrada.")
