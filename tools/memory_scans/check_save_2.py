import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
# O outro struct
struct_addr = 0x3b35c7e0 

print(f"Escanendo Save Struct Outro ({hex(struct_addr)})...")
try:
    data = pm.read_bytes(struct_addr, 0x100)
    name = data[0x50:0x60].split(b'\x00')[0].decode('utf-8', errors='ignore')
    print(f"Nome (+0x50): {name}")
    wtype = struct.unpack('<I', data[0x74:0x78])[0]
    print(f"Tipo (+0x74): {wtype}")
except Exception as e:
    print(f"Erro: {e}")
