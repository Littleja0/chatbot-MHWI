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

# Pointer chain para a arma viva
weapon_ptr = follow(base + 0x050139A0, [0x50, 0xC0, 0x8, 0x78])

if weapon_ptr:
    print(f"Instancia de Arma Encontrada em: {hex(weapon_ptr)}")
    data = pm.read_bytes(weapon_ptr, 0x1000)
    
    # Vamos buscar o TIPO (sabemos que Martelo = 4, LS = 3, CB = 9)
    # E vamos buscar os IDs prováveis: 779, 2103, 2738, 2412, etc.
    targets = {
        779: "Gigagelo II",
        2103: "Sabre Oculto+",
        2738: "Fortaleza Cromada I",
        2412: "Maça Palácio",
        2490: "Bardo Palácio",
        2244: "Espada Palácio"
    }
    
    # Scan por Int32 (Weapon ID)
    for i in range(0, 0x1000 - 4, 1): # Scan byte by byte
        val = struct.unpack('<I', data[i:i+4])[0]
        if val in targets:
            print(f"  🎯 ACHADO ID {val} ({targets[val]}) no WeaponObject + {hex(i)}")
        # Check Type (4, 3, or 9)
        if val in [3, 4, 9]:
            # Verificar se não é um ID gigante
            print(f"  ❓ Candidato a Tipo ({val}) no WeaponObject + {hex(i)}")

else:
    print("Arma viva não encontrada.")
