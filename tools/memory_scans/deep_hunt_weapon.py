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

# Testar se o pointer chain da arma está vindo pro lugar certo
# A arma viva (objeto) tem vida, afiação, etc.
ptr_chain = [0x50, 0xC0, 0x8, 0x78]
obj = follow(base + 0x050139A0, ptr_chain)

if obj:
    print(f"Objeto de Arma Viva: {hex(obj)}")
    # Vamos ler os primeiros 32KB do objeto
    # E vamos buscar os IDs que o usuário confirmou estar usando AGORA:
    # Digamos que ele esteja de Martelo Gigagelo II (779) ou LS Sabre Oculto+ (2103)
    targets = [779, 2103, 2738, 2412, 2804, 2244, 2490]
    
    buf = pm.read_bytes(obj, 0x8000)
    print("Escaneando objeto por IDs de arma...")
    for i in range(0, len(buf)-4, 1):
        v = struct.unpack('<I', buf[i:i+4])[0]
        if v in targets:
            print(f"  🎯 ACHADO ID {v} no offset +{hex(i)}")
        # Também checar shorts
        s = struct.unpack('<H', buf[i:i+2])[0]
        if s in targets:
            print(f"  🎯 ACHADO SHORT {s} no offset +{hex(i)}")

    # Se não achou nada, talvez a arma esteja em outro ponteiro
    # Vamos checar o offset 0x2E8 (Tipo)
    wtype = struct.unpack('<I', buf[0x2E8:0x2EC])[0]
    print(f"Tipo em +0x2E8: {wtype}")
    
else:
    print("Objeto de arma não encontrado.")
