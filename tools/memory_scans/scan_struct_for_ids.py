import sys
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
struct_addr = 0x95c598d0

print(f"Dumping suspected player struct at {hex(struct_addr)} and filtering for potential IDs...")

# Range expanded to 8KB
for i in range(0, 0x2000, 4):
    try:
        val = pm.read_int(struct_addr + i)
        # Armor IDs are usually between 1 and 2500
        if 1 <= val <= 2500:
            # Let's see if we find any known IDs
            tag = ""
            if val == 1457: tag = " <-- HEAD?"
            if val == 1463: tag = " <-- CHEST?"
            if val == 884: tag = " <-- ARMS?"
            if val == 1155: tag = " <-- WAIST?"
            if val == 1466: tag = " <-- LEGS?"
            if val == 6: tag = " <-- CHARM?"
            if val == 2103: tag = " <-- WEAPON?"
            
            print(f"  +{hex(i)}: {val}{tag}")
    except: pass
