from backend.memory_reader import get_reader, WEAPON_ID_OFFSETS, WEAPON_TYPES
import time

def diagnose_offsets():
    reader = get_reader()
    if not reader.connect(): return

    print("--- DIAGNÓSTICO DE CATEGORIAS ---")
    base = reader.base
    
    # 1. Ler o TIPO ATIVO pelo ponteiro vivo
    # Esse é o único que o jogo GARANTE que é a arma na sua mão
    w_ptr = reader._read_ptr_chain(0x050139A0, [0x50, 0xC0, 0x8, 0x78])
    if w_ptr:
        live_type = reader._ri32(w_ptr + 0x2E8)
        print(f"Tipo Vivo (Pointer Chain): {live_type} ({WEAPON_TYPES.get(live_type, 'UNK')})")
        # Vamos ler o que tem perto do live_type
        context = reader.pm.read_bytes(w_ptr + 0x2E0, 32)
        print(f"Contexto no objeto da arma: {context.hex(' ')}")
    
    # 2. Verificar o que tem em cada offset estático que eu tinha mapeado
    print("\nVerificando offsets da 'Tabela Estática' (os suspeitos do erro):")
    for tid, offset in WEAPON_ID_OFFSETS.items():
        val = reader._ri32(base + offset)
        print(f"  Tipo {tid} ({WEAPON_TYPES[tid]}): End:{hex(base+offset)} Val:{val}")

if __name__ == "__main__":
    diagnose_offsets()
