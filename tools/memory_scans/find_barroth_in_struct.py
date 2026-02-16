from backend.memory_reader import get_reader
import struct

def find_weapon_in_struct():
    reader = get_reader()
    if not reader.connect(): return
    
    addr = reader.find_player_struct()
    if not addr: return
    
    print(f"Buscando IDs de 'Fatiador de Barroth I' (2224) e Tipo (1) no struct {hex(addr)}...")
    data = reader.pm.read_bytes(addr, 0x1000)
    
    for i in range(0, 0x1000 - 4, 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        if val == 2224:
            print(f"  [!] ID 2224 encontrado no OFFSET {hex(i)}")
            # Ver o que tem perto
            if i >= 4:
                prev = struct.unpack('<I', data[i-4:i])[0]
                print(f"      Valor anterior (Tipo?): {prev}")
        if val == 1:
            # Muitos '1's podem aparecer, mas vamos olhar os que estão perto de IDs de armas
            pass

if __name__ == "__main__":
    find_weapon_in_struct()
