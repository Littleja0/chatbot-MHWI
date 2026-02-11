import os
import hashlib
import json
import requests # type: ignore
import gdown # type: ignore
from pathlib import Path
from dotenv import load_dotenv # type: ignore

load_dotenv()

# Configurações via .env
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "1gv74vwcprFXaLECmvKnoP9uQsKBZVfau")
MANIFEST_FILE_ID = os.getenv("MANIFEST_FILE_ID", "1ISgFunL29T0IlzzDo7ufEGMkwNE1FGjk")
# Versão base definida no .env
APP_VERSION_LOCAL = os.getenv("APP_VERSION", "1.0.0")

# Link direto para o manifest.json dentro do Drive (para verificação rápida)
MANIFEST_DRIVE_URL = f"https://drive.google.com/uc?export=download&id={MANIFEST_FILE_ID}"

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
        # 1. Checagem rápida de versão via manifest.json
        report("� Checando versão remota...", 15)
        response = requests.get(MANIFEST_DRIVE_URL, timeout=10)
        if response.status_code == 200:
            remote_manifest = response.json()
            remote_version = remote_manifest.get("version", "0.0.0")
            
            # Prioridade de versão local: .env > manifest.json
            local_version = APP_VERSION_LOCAL
            if os.path.exists("manifest.json"):
                try:
                    with open("manifest.json", "r") as f:
                        file_version = json.load(f).get("version", "0.0.0")
                        # Se o arquivo for mais recente, usa ele
                        local_version = file_version
                except: pass

            if remote_version == local_version:
                report(f"✅ Versão atualizada ({local_version})", 100)
                return True
            
            report(f"✨ Nova versão detectada: {remote_version}", 20)
        
        # 2. Se as versões forem diferentes (ou falhar a checagem), sincroniza
        report("📦 Sincronizando arquivos com o Drive (via gdown)...", 30)
        url = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
        
        # O uso de use_cookies=False às vezes ajuda a evitar bloqueios do Google
        output = gdown.download_folder(url, quiet=False, use_cookies=False, remaining_ok=True)
        
        if output:
            report("✅ Sincronização concluída!", 100)
            return True
        else:
            report("❌ Falha ao sincronizar pasta do Drive.", 100)
            return False

    except Exception as e:
        error_msg = str(e)
        # Simplificando para evitar problemas com o linter Pyre2
        report(f"❌ Erro no Update: {error_msg}", 100)
        return False

if __name__ == "__main__":
    # Para teste manual
    # update_app()
    pass
