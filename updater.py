import os
import hashlib
import json
import requests
import gdown
from pathlib import Path

# ID da pasta do Google Drive (MHWUpdate)
DRIVE_FOLDER_ID = "1gv74vwcprFXaLECmvKnoP9uQsKBZVfau"
# Link direto para o manifest.json dentro do Drive (para verificação rápida)
MANIFEST_DRIVE_URL = "https://drive.google.com/uc?export=download&id=1ISgFunL29T0IlzzDo7ufEGMkwNE1FGjk"

def get_file_hash(path):
    if not os.path.exists(path):
        return None
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def update_app(progress_callback=None):
    def report(text, progress):
        if progress_callback:
            progress_callback(text, progress)
        print(f"[{progress}%] {text}")

    report("🔍 Verificando atualizações no Google Drive...", 10)
    
    # Tentativa de ler a versão remota sem baixar tudo ainda
    # Se você quiser simplificar, pode pular essa checagem e baixar direto
    # mas o gdown baixará a pasta toda se houver mudanças.
    
    try:
        report("📦 Sincronizando arquivos com o Drive (via gdown)...", 30)
        
        # O gdown --folder sincroniza a pasta atual com a do drive
        # Ele só baixa o que mudou, de forma inteligente.
        url = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
        
        # Baixa a pasta diretamente na raiz do projeto
        # gdown cuida de extrair e organizar
        output = gdown.download_folder(url, quiet=True, use_cookies=False, remaining_ok=True)
        
        if output:
            report("✅ Sincronização concluída!", 100)
            return True
        else:
            report("❌ Falha ao sincronizar pasta do Drive.", 100)
            return False

    except Exception as e:
        error_msg = str(e)
        report(f"❌ Erro no Update: {error_msg[:50]}", 100)
        return False

if __name__ == "__main__":
    # Para teste manual
    # update_app()
    pass
