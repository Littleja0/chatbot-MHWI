import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
# Endereço do jogador que achamos antes e que é estável
player_addr = 0x95c598d0 

# IDs das armas que você mencionou estar usando agora:
# Gigagelo II (Martelo): 779
# Sabre Oculto+ (LS): 2103
# Maça Palácio (Martelo): 2412

targets = {
    779: "Gigagelo II (Hammer)",
    2103: "Sabre Oculto+ (LS)",
    2412: "Maça Palácio (Hammer)"
}

print(f"Buscando IDs ativos no Player Struct ({hex(player_addr)})...")

# Escaneando 128KB ao redor do struct do player para achar o slot de EQUIPAMENTO ATUAL
try:
    data = pm.read_bytes(player_addr, 0x20000)
    for i in range(0, len(data)-4, 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        if val in targets:
            print(f"  🎯 ACHADO: {targets[val]} ID({val}) no offset: player + {hex(i)}")
            
            # Se achou a arma, vamos olhar o que tem perto (tipo, etc)
            context = struct.unpack('<IIII', data[i:i+16])
            print(f"     Contexto (+0x0 to +0x10): {context}")
except Exception as e:
    print(f"Erro ao ler: {e}")
