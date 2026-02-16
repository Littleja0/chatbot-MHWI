import sys
from pymem import Pymem

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

# Testar HR/MR via chain
lvl_addr = follow(base + 0x05013950, [0xA8])
if lvl_addr:
    hr = pm.read_int(lvl_addr)
    mr = pm.read_int(lvl_addr + 0x4)
    print(f"Chain Level Results: HR={hr}, MR={mr} (Addr: {hex(lvl_addr)})")
else:
    print("Chain Level Failed.")

# Testar Zone
zone_addr = follow(base + 0x0500ECA0, [0xAED0])
if zone_addr:
    zone = pm.read_int(zone_addr)
    print(f"Chain Zone Results: {zone} (Addr: {hex(zone_addr)})")
else:
    print("Chain Zone Failed.")
