import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

# IDs que você confirmou:
# 779 = Gigagelo II (Hammer)
# 2103 = Sabre Oculto+ (LS)
# 2738 = Fortaleza Cromada I (CB)
targets = [779, 2103, 2738]

# Região provável do Save (baseado nos escaneamentos anteriores)
search_start = 0x95c00000
search_end   = 0x95d00000

print(f"Buscando IDs {targets} na região {hex(search_start)}...")

try:
    data = pm.read_bytes(search_start, search_end - search_start)
    for tid in targets:
        t_bytes = struct.pack('<H', tid) # Procurando como Short (2 bytes)
        idx = data.find(t_bytes)
        while idx != -1:
            abs_addr = search_start + idx
            print(f"  🎯 ACHADO ID {tid} em {hex(abs_addr)} (Offset relativo ao bloco: {hex(idx)})")
            
            # Verificando se o tipo da arma está por perto
            # Tipo 4 (Martelo), 3 (LS), 9 (CB)
            nearby = pm.read_bytes(abs_addr - 16, 32)
            print(f"     Contexto hex: {nearby.hex(' ')}")
            
            idx = data.find(t_bytes, idx + 2)
except Exception as e:
    print(f"Erro: {e}")
