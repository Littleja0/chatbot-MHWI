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

# Endereço base do sistema de equipamentos
weapon_ptr_base = base + 0x050139A0
weapon_type_addr = follow(weapon_ptr_base, [0x50, 0xC0, 0x8, 0x78, 0x2E8])

print(f"Live Weapon Type Addr: {hex(weapon_type_addr) if weapon_type_addr else 'Failed'}")

target_ids = [1457, 1463, 884, 1155, 1466, 6]
target_weapon = 2103

if weapon_type_addr:
    print(f"Scanning around {hex(weapon_type_addr)} for armor IDs {target_ids}...")
    # Scan a wider range around weapon type
    for d in range(-0x2000, 0x5000, 4):
        try:
            val = pm.read_int(weapon_type_addr + d)
            if val in target_ids or val == target_weapon:
                print(f"  FOUND {val} at type_addr + {hex(d)}")
        except: pass

# Also try searching near the EQUIPMENT chain
# Chain: [0x50, 0x80, 0x80, 0x18, 0x460]
equip_addr = follow(weapon_ptr_base, [0x50, 0x80, 0x80, 0x18, 0x460])
print(f"\nLive Equipment Addr: {hex(equip_addr) if equip_addr else 'Failed'}")
if equip_addr:
    print(f"Scanning around {hex(equip_addr)} for armor IDs...")
    for d in range(-0x200, 0x500, 4):
        try:
            val = pm.read_int(equip_addr + d)
            if val in target_ids or val == target_weapon:
                print(f"  FOUND {val} at equip_addr + {hex(d)}")
        except: pass
