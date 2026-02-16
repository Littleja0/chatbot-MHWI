from backend.memory_reader import get_reader
import struct

def scan_weapon_ptr_context():
    reader = get_reader()
    if not reader.connect(): return
    
    # [0x50, 0xC0, 0x8, 0x78] é o ponteiro para o objeto 'Player' em combate
    player_ptr = reader._read_ptr_chain(0x050139A0, [0x50, 0xC0, 0x8, 0x78])
    if not player_ptr:
        print("Não achei o player_ptr.")
        return
        
    print(f"Player Pointer em combate: {hex(player_ptr)}")
    print("Escaneando offsets em busca de 2224 (ID) e 1 (Tipo)...")
    
    # Scan de 0x0 a 0x1000 dentro do objeto player
    data = reader.pm.read_bytes(player_ptr, 0x1000)
    for i in range(0, 0x1000 - 4, 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        if val == 1:
            # Se for tipo 1, vamos ver se o ID 2224 está perto
            # No MHW, o ID da arma geralmente está no offset +0x0 de um objeto apontado por aqui
            potential_obj_ptr = struct.unpack('<Q', data[i-12 : i-4] if i>=12 else b'\x00'*8)[0]
            # Vamos simplificar: apenas ver se 1 e 2224 estão perto no próprio struct
            pass
        if val == 2224:
            print(f"  [!] ID 2224 encontrado no OFFSET {hex(i)}")
        
        # Testar se algum offset aqui é um ponteiro para a arma
        if i % 8 == 0:
            ptr = struct.unpack('<Q', data[i:i+8])[0]
            if ptr > 0x140000000 and ptr < 0x300000000:
                try:
                    # Ler o que tem nesse ponteiro
                    w_id = reader.pm.read_int(ptr)
                    w_type = reader.pm.read_int(ptr + 4)
                    if w_id == 2224 and w_type == 1:
                        print(f"  [⭐] PONTEIRO PARA ARMA ATIVA ACHADO NO OFFSET {hex(i)} -> {hex(ptr)}")
                        print(f"      Isso confirma: player_ptr + {hex(i)} aponta para ID {w_id} Tipo {w_type}")
                except: pass

if __name__ == "__main__":
    scan_weapon_ptr_context()
