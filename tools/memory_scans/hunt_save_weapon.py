from backend.memory_reader import get_reader, STRUCT_OFFSETS
import struct

def find_active_weapon_id():
    reader = get_reader()
    if not reader.connect(): return

    print("--- BUSCANDO ARMA NO SLOT DE EQUIPAMENTO ---")
    struct_addr = reader.find_player_struct()
    if not struct_addr:
        print("Não foi possível localizar o struct do jogador.")
        return

    # No MHW, o equipamento ativo geralmente fica em blocos de struct.
    # Vamos ler uma área grande ao redor do Tipo (0x74)
    data = reader.pm.read_bytes(struct_addr, 0x300)
    
    # O Tipo está em +0x74
    w_type = struct.unpack('<I', data[0x74:0x78])[0]
    
    # Vamos procurar o ID ativo. Costuma estar muito perto do tipo.
    # Geralmente ID da arma está em +0x78 ou em uma lista de equipamentos em +0x100...
    potential_id_1 = struct.unpack('<I', data[0x78:0x7C])[0]
    
    print(f"Tipo detectado no save: {w_type}")
    print(f"ID detectado no offset +0x78: {potential_id_1}")
    
    # Vamos escanear os próximos bytes em busca de IDs conhecidos
    # (Sabre Oculto+=2103, Maça Palácio=2412, etc)
    for i in range(0x70, 0x200, 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        if val in [2103, 2412, 779, 2297]: # IDs que você usou/comentou
            print(f"  ⭐ ACHADO! ID {val} no OFFSET {hex(i)}")

if __name__ == "__main__":
    find_active_weapon_id()
