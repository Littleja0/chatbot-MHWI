import sys, struct
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

# O ponteiro que provou ser real-time para a arma
live_ptr_base = follow(base + 0x050139A0, [0x50, 0xC0, 0x8, 0x78])
if not live_ptr_base:
    print("Falha ao pegar live_ptr_base")
    sys.exit()

# O tipo fica em +0x2E8 relativo a esse base
# Vamos escanear 32KB ao redor desse live_ptr_base
print(f"Scanning 64KB around Live Ptr Base ({hex(live_ptr_base)})...")
targets = [1457, 1463, 884, 1155, 1466, 6]

try:
    data = pm.read_bytes(live_ptr_base - 0x8000, 0x10000)
    for t in targets:
        t_bytes = struct.pack('<I', t)
        idx = data.find(t_bytes)
        while idx != -1:
            rel = idx - 0x8000
            print(f"  FOUND {t} at live_ptr_base {rel:+06x}")
            idx = data.find(t_bytes, idx + 4)
except Exception as e:
    print(f"Error: {e}")
