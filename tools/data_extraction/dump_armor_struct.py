import sys
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
addr = 0x9586090c 

print(f"Dumping armor struct at {hex(addr)}...")
for i in range(0, 0x50, 4):
    try:
        val = pm.read_int(addr + i)
        print(f"  +{hex(i)}: {val} ({hex(val) if val >= 0 else val})")
    except: pass
