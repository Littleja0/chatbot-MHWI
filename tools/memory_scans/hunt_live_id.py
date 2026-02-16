import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

# Endereço conhecido do player struct
player_addr = 0x95c598d0 

# IDs Reais (confirmados pelo usuário/banco)
# Gigagelo II (Martelo, Tipo 4): 779
# Sabre Oculto+ (LS, Tipo 3): 2103
# Fortaleza Cromada I (CB, Tipo 9): 2738

print(f"Examinando Player Struct em {hex(player_addr)}...")

try:
    # Vamos ler 16KB do struct
    data = pm.read_bytes(player_addr, 0x4000)
    
    # Busca por ID 779, 2103 ou 2738
    targets = {779: "Gigagelo II (Hammer/4)", 2103: "Sabre Oculto+ (LS/3)", 2738: "Fortaleza Cromada (CB/9)"}
    
    for offset in range(0, len(data)-4, 1): # Scan byte by byte to be sure
        val = struct.unpack('<I', data[offset:offset+4])[0]
        if val in targets:
            print(f"  [FOUND] {targets[val]} em player + {hex(offset)}")
            # Checar se o TIPO da arma está por perto (como int32 ou int8)
            # Se for Martelo (Tipo 4), procure por 4 por perto
            nearby = data[max(0, offset-32) : min(len(data), offset+32)]
            print(f"     Valores próximos (hex): {nearby.hex(' ')}")

except Exception as e:
    print(f"Erro: {e}")

# Também vamos tentar seguir a pointer chain da arma novamente
def follow(b_addr, offsets):
    try:
        addr = pm.read_longlong(b_addr)
        for o in offsets[:-1]:
            addr = pm.read_longlong(addr + o)
            if not addr: return 0
        return addr + offsets[-1]
    except: return 0

weapon_obj = follow(base + 0x050139A0, [0x50, 0xC0, 0x8, 0x78])
if weapon_obj:
    print(f"\nWeapon Object encontrado em: {hex(weapon_obj)}")
    w_data = pm.read_bytes(weapon_obj, 0x1000)
    # Scan por IDs no objeto da arma
    for offset in range(0, 0x1000-4, 4):
        val = struct.unpack('<I', w_data[offset:offset+4])[0]
        if val in targets:
             print(f"  [FOUND] {targets[val]} no WeaponObject + {hex(offset)}")
else:
    print("\nWeapon Object não encontrado.")
