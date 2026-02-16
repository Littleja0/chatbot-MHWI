import sys, struct
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
struct_addr = 0x95c598d0

print(f"Dumping suspected player struct at {hex(struct_addr)} (SCANNING SHORTS)...")

# IDs equipados
targets = [1457, 1463, 884, 1155, 1466, 6]

for i in range(0, 0x4000, 2):
    try:
        val = pm.read_short(struct_addr + i)
        if val in targets:
            tag = ""
            if val == 1457: tag = " <-- HEAD"
            if val == 1463: tag = " <-- CHEST"
            if val == 884: tag = " <-- ARMS"
            if val == 1155: tag = " <-- WAIST"
            if val == 1466: tag = " <-- LEGS"
            if val == 6: tag = " <-- CHARM"
            
            # Check for weapon ID nearby
            weapon_val = pm.read_short(struct_addr + i - 0x10) # Just guessing
            
            print(f"  +{hex(i)}: {val}{tag}")
    except: pass
