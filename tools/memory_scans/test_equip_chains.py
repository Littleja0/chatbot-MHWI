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

# Testar varias chains de equipamento comuns
chains = [
    [0x50, 0x80, 0x80, 0x18, 0x460],
    [0x50, 0x90, 0x10, 0x18, 0x460],
    [0x50, 0x80, 0x10, 0x18, 0x460],
    [0x50, 0xC0, 0x8, 0x78, 0x460]
]

for c in chains:
    addr = follow(base + 0x050139A0, c)
    if addr:
        ids = []
        for i in range(5):
            ids.append(pm.read_int(addr + (i*4)))
        print(f"Chain {c} -> {ids} at {hex(addr)}")
