import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')

# Onde o Zenny costumava estar
old_zenny_addr = 0x95c59968 
zenny_val = 598959

try:
    current_val = pm.read_int(old_zenny_addr)
    print(f"Valor em {hex(old_zenny_addr)}: {current_val}")
    if current_val == zenny_val:
        print("✅ ZENNY AINDA ESTÁ AQUI!")
    else:
        print("❌ Zenny mudou. Buscando novo local do Zenny...")
        # Scan range similar
        for addr in range(0x10000000, 0x100000000, 0x10000):
            try:
                data = pm.read_bytes(addr, 0x10000)
                idx = data.find(struct.pack('<I', zenny_val))
                if idx != -1:
                    print(f"  ⭐ ZENNY ENCONTRADO EM {hex(addr + idx)}")
                    # Examine the whole 320KB struct
                    new_struct = addr + idx - 0x98
                    print(f"  Novo Struct: {hex(new_struct)}")
                    # Scan ID do Gigagelo II (779) no struct
                    struct_buf = pm.read_bytes(new_struct, 0x20000)
                    for i in range(0, len(struct_buf)-4, 1):
                        v = struct.unpack('<I', struct_buf[i:i+4])[0]
                        if v == 779:
                             print(f"    🎯 ID 779 ENCONTRADO em struct + {hex(i)}")
                        if v == 2103:
                             print(f"    🎯 ID 2103 ENCONTRADO em struct + {hex(i)}")
            except: pass
except Exception as e:
    print(f"Erro: {e}")
