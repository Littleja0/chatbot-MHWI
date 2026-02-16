from backend.memory_reader import get_reader
import time

def validate():
    print("--- VALIDANDO GOJO (ARMA ATUAL) ---")
    reader = get_reader()
    if not reader.connect():
        print("Erro ao conectar ao MHW.")
        return

    # Tenta ler 5 vezes para ver se está estável
    for i in range(5):
        weapon = reader.get_weapon_info()
        player = reader.get_player_info()
        
        print(f"\nTentativa {i+1}:")
        print(f"  Jogador: {player['name']} (HR {player['hr']} / MR {player['mr']})")
        if weapon:
            print(f"  Arma: {weapon['name']} (ID {weapon['id']})")
            print(f"  Tipo: {weapon['type']}")
            if weapon['sharpness']:
                print(f"  Afiação detectada: {weapon['sharpness'][0] if isinstance(weapon['sharpness'], list) else weapon['sharpness']}")
        else:
            print("  Arma: NÃO DETECTADA")
        
        time.sleep(1)

if __name__ == "__main__":
    validate()
