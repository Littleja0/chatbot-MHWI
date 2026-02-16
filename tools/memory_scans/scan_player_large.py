from backend.memory_reader import get_reader
import struct

def find_any_weapon_id():
    reader = get_reader()
    if not reader.connect(): return
    
    struct_addr = reader.find_player_struct()
    print(f"Lendo 0x10000 bytes a partir de {hex(struct_addr)}...")
    
    # Vamos ler um bloco maior (64KB) para garantir que pegamos o inventário/equipamento
    data = reader.pm.read_bytes(struct_addr, 0x10000)
    
    target_id = 2224 # Fatiador de Barroth I
    target_type = 1
    
    for i in range(0, len(data) - 8, 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        if val == target_id:
            # Ver se o tipo está perto
            type_near = struct.unpack('<I', data[i+4:i+8])[0]
            if type_near == target_type:
                print(f"  [FOUND] ID {val} + Tipo {type_near} no OFFSET {hex(i)}")
                # Vamos ver o que tem antes (provavelmente o slot ou algo assim)
                ctx = data[i-16:i+16].hex(' ')
                print(f"     Contexto: {ctx}")

if __name__ == "__main__":
    find_any_weapon_id()
