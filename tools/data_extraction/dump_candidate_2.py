import sys
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
addr = 0x27fdb4914

print(f"Dumping around candidate {hex(addr)}...")
for i in range(-0x100, 0x100, 4):
    try:
        val = pm.read_int(addr + i)
        print(f"  {i:+04x}: {val}")
    except: pass
