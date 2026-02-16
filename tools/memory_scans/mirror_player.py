import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
player_addr = 0x95c598d0 

print(f"--- ESPELHO DO PLAYER STRUCT ({hex(player_addr)}) ---")
try:
    data = pm.read_bytes(player_addr, 0x200) # Primeiros 512 bytes
    
    print(f"Nome (+0x50): {data[0x50:0x60].split(b'\x00')[0].decode('utf-8', errors='ignore')}")
    print(f"Tipo Arma (+0x74): {struct.unpack('<I', data[0x74:0x78])[0]}")
    
    print("\nValores suspectos (ID de arma?):")
    # Vamos listar todos os ints de 4 bytes entre +0x70 e +0x150
    for i in range(0x70, 0x150, 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        # Se o valor for um ID plausível (entre 1 e 5000)
        if 0 < val < 10000:
            print(f"  Offset +{hex(i)}: {val}")

    # E se for short?
    print("\nBusca por Shorts (2 bytes):")
    for i in range(0x70, 0x150, 2):
        val = struct.unpack('<H', data[i:i+2])[0]
        if val in [779, 2103, 2738]:
            print(f"  ⭐ ACHADO SHORT {val} no Offset +{hex(i)}")

except Exception as e:
    print(f"Erro: {e}")
