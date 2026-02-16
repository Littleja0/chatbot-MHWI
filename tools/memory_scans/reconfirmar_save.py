import sys, struct, time
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')

def find_player_struct():
    # Busca o nome pra achar a base do save
    print("Buscando struct do jogador pelo nome 'LittleJ'...")
    for addr in range(0x10000000, 0xA0000000, 0x10000):
        try:
            data = pm.read_bytes(addr, 0x10000)
            idx = data.find(b"LittleJ\x00")
            if idx != -1:
                # Achamos o nome. Geralmente o HR/MR/Zenny estão por perto
                # Vamos verificar se o Zenny esperado (598959) está perto
                # O Zenny fica em +0x10 ou algo assim do nome? Vamos ver.
                abs_addr = addr + idx
                print(f"  Encontrado 'LittleJ' em {hex(abs_addr)}")
                # O Zenny (598959 como 4 bytes)
                zenny_bytes = struct.pack('<I', 598959)
                if zenny_bytes in data:
                    print(f"  ⭐ CONFIRMADO: Zenny 598959 encontrado no mesmo bloco!")
                    return abs_addr - 0x50 # Ajuste comum para o início do struct
        except: pass
    return None

base_addr = find_player_struct()
if base_addr:
    print(f"Endereço Base Sugerido: {hex(base_addr)}")
    
    # Agora vamos ler o que tem por perto e tentar achar o ID da sua arma ATUAL
    # Se você está com o Martelo Gigagelo II (ID 779)
    print("Escaneando arredores por ID 779 ou 2103...")
    data = pm.read_bytes(base_addr, 0x10000)
    for i in range(0, len(data)-4, 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        if val in [779, 2103, 2738, 2412, 2490]:
            print(f"  EQUIPADO? ID {val} encontrado em base + {hex(i)}")
            # Vamos mostrar o contexto
            context = struct.unpack('<IIII', data[i:i+16])
            print(f"     Contexto: {context}")
else:
    print("Não foi possível localizar o struct do jogador.")
