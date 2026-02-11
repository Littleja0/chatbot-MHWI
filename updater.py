import os
import hashlib
import json
import requests # type: ignore
from pathlib import Path

# Configuração de atualização via GitHub (Caminho A - Alta Velocidade)
# O link deve apontar para onde os arquivos COMPILADOS estão no seu GitHub
MANIFEST_URL = "https://raw.githubusercontent.com/Littleja0/chatbot-MHWI/main/dist/MHWChatbot/manifest.json"
BASE_DOWNLOAD_URL = "https://raw.githubusercontent.com/Littleja0/chatbot-MHWI/main/dist/MHWChatbot/"

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

    report("🔍 Verificando atualizações...", 10)
    try:
        response = requests.get(MANIFEST_URL, timeout=10)
        if response.status_code != 200:
            print("Não foi possível acessar o servidor de atualizações.")
            return

        remote_manifest = response.json()
        remote_version = remote_manifest.get("version", "0.0.0")
        
        # Carregar versão local
        local_version = "0.0.0"
        if os.path.exists("manifest.json"):
            with open("manifest.json", "r") as f:
                local_version = json.load(f).get("version", "0.0.0")

        if remote_version == local_version:
            report(f"✅ Versão atualizada ({local_version})", 100)
            return True
        
        report(f"✨ Nova versão disponível: {remote_version}", 20)
        
        files_to_update = []
        for file_path, remote_hash in remote_manifest["files"].items():
            local_hash = get_file_hash(file_path)
            if local_hash != remote_hash:
                files_to_update.append(file_path)

        if not files_to_update:
            report("Arquivos já estão sincronizados.", 100)
            return True

        count = len(files_to_update)
        report(f"📦 Baixando {count} arquivos...", 30)
        
        for i, file_path in enumerate(files_to_update):
            prog = 30 + int((i / count) * 60)
            report(f"📥 Baixando: {Path(file_path).name}", prog)
            # Criar pastas se não existirem
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Download do arquivo
            file_url = f"{BASE_DOWNLOAD_URL}{file_path}"
            r = requests.get(file_url, stream=True)
            if r.status_code == 200:
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                print(f"❌ Falha ao baixar {file_path}: Status {r.status_code}")

        # Salvar o novo manifesto localmente
        with open("manifest.json", "w") as f:
            json.dump(remote_manifest, f, indent=4)

        report(f"🎉 Atualização para v{remote_version} concluída!", 100)
        return True

    except Exception as e:
        report(f"❌ Erro: {str(e)}", 100)
        return False

if __name__ == "__main__":
    # Para teste manual
    # update_app()
    pass
