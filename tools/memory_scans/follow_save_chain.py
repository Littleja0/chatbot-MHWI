import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

# Ponto de partida: Session Pointer
# MonsterHunterWorld.exe + 0x050139A0 -> 0x50
session_ptr = pm.read_longlong(base + 0x050139A0)
if session_ptr:
    session_ptr = pm.read_longlong(session_ptr + 0x50)
    print(f"Session Player Pointer: {hex(session_ptr)}")
    
    # Vamos explorar o Pointer 0x2b9517f68 (que achamos antes)
    # E vamos explorar o Session Pointer
    
    # O save atual costuma estar em base + 0x050139A0 -> 0x50 -> 0x20 -> 0x70 -> 0x50 -> 0x10...
    save_chain = [0x50, 0x20, 0x70, 0x50, 0x10]
    curr = pm.read_longlong(base + 0x050139A0)
    for off in save_chain:
        try:
            curr = pm.read_longlong(curr + off)
            print(f"  Follow {hex(off)} -> {hex(curr)}")
        except:
            print(f"  Failed at {hex(off)}")
            break
    
    # No endereço final curr, procure o nome
    try:
        name = pm.read_bytes(curr + 0x50, 16).split(b'\x00')[0].decode('utf-8')
        print(f"Nome no pointer chain: {name}")
    except: pass
else:
    print("Session not found.")
