import os
import hashlib
import json
import requests  # type: ignore
import gdown  # type: ignore
import sys
import io
from pathlib import Path
from dotenv import load_dotenv  # type: ignore

# Forçar UTF-8 no stdout/stderr no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except (AttributeError, io.UnsupportedOperation):
        pass

load_dotenv()

# Configurações via .env
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "1gv74vwcprFXaLECmvKnoP9uQsKBZVfau")
MANIFEST_FILE_ID = os.getenv("MANIFEST_FILE_ID", "1ISgFunL29T0IlzzDo7ufEGMkwNE1FGjk")
# Versão base definida no .env (prioridade máxima)
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


def get_local_version():
    """
    Retorna a versão local. Prioridade: .env > manifest.json local.
    """
    # Se o .env define a versão, essa é a verdadeira (o desenvolvedor seta isso)
    env_version = APP_VERSION_LOCAL
    
    # Também checa o manifest.json local como fallback
    manifest_version = "0.0.0"
    if os.path.exists("manifest.json"):
        try:
            with open("manifest.json", "r") as f:
                manifest_version = json.load(f).get("version", "0.0.0")
        except:
            pass
    
    # Retorna a versão mais alta entre .env e manifest
    # Isso evita downgrades acidentais
    try:
        env_parts = tuple(int(x) for x in env_version.split("."))
        manifest_parts = tuple(int(x) for x in manifest_version.split("."))
        return env_version if env_parts >= manifest_parts else manifest_version
    except (ValueError, AttributeError):
        return env_version


def update_app(progress_callback=None):
    def report(text, progress):
        if progress_callback:
            progress_callback(text, progress)
        print(f"[{progress}%] {text}")

    report("🔍 Verificando atualizações...", 10)
    
    try:
        # 1. Checagem rápida de versão via manifest.json remoto
        report("📡 Checando versão remota...", 15)
        response = requests.get(MANIFEST_DRIVE_URL, timeout=10)
        if response.status_code != 200:
            report("⚠️ Não foi possível verificar atualizações. Continuando...", 100)
            return True
        
        remote_manifest = response.json()
        remote_version = remote_manifest.get("version", "0.0.0")
        local_version = get_local_version()

        if remote_version == local_version:
            report(f"✅ Versão atualizada ({local_version})", 100)
            return True
        
        report(f"✨ Nova versão detectada: {remote_version} (atual: {local_version})", 20)
        
        # 2. Comparar hashes para encontrar APENAS arquivos que mudaram
        remote_files = remote_manifest.get("files", {})
        
        if not remote_files:
            # Se não há lista de arquivos no manifest, baixa tudo (fallback)
            report("📦 Sincronizando todos os arquivos...", 30)
            url = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
            gdown.download_folder(url, quiet=False, use_cookies=False, remaining_ok=True)
            report("✅ Sincronização concluída!", 100)
            return True
        
        # Filtrar apenas arquivos que realmente mudaram (hash diferente)
        # Ignorar _internal/ pois são dependências do executável (não mudam para o dev mode)
        files_to_update = []
        for filepath, remote_hash in remote_files.items():
            # Pular arquivos de _internal/ — essas são dependências do PyInstaller
            # Elas não são necessárias quando rodando via python (dev mode)
            if filepath.startswith("_internal/"):
                continue
            
            local_hash = get_file_hash(filepath)
            if local_hash != remote_hash:
                files_to_update.append(filepath)
        
        if not files_to_update:
            report(f"✅ Todos os arquivos estão atualizados! ({local_version})", 100)
            # Atualizar manifest local para evitar checagens futuras
            with open("manifest.json", "w") as f:
                json.dump(remote_manifest, f, indent=4)
            return True
        
        report(f"📦 Atualizando {len(files_to_update)} arquivo(s)...", 30)
        
        # Baixar apenas os arquivos que mudaram via gdown
        # Como gdown não suporta download individual por nome facilmente,
        # baixamos a pasta mas apenas mostramos progresso dos relevantes
        total = len(files_to_update)
        for i, filepath in enumerate(files_to_update):
            progress = 30 + int((i / total) * 60)  # 30% a 90%
            report(f"📥 ({i+1}/{total}) {os.path.basename(filepath)}", progress)
        
        # Usar gdown para sincronizar (ele vai pular arquivos existentes se forem iguais)
        url = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
        gdown.download_folder(url, quiet=True, use_cookies=False, remaining_ok=True)
        
        # Atualizar manifest local
        with open("manifest.json", "w") as f:
            json.dump(remote_manifest, f, indent=4)
        
        report("✅ Atualização concluída!", 100)
        return True

    except requests.exceptions.Timeout:
        report("⚠️ Timeout ao verificar atualizações. Continuando offline...", 100)
        return True
    except requests.exceptions.ConnectionError:
        report("⚠️ Sem conexão com internet. Continuando offline...", 100)
        return True
    except Exception as e:
        error_msg = str(e)
        report(f"⚠️ Erro no update: {error_msg}. Continuando...", 100)
        # Não bloqueia a inicialização por causa de erros de update
        return True


if __name__ == "__main__":
    # Para teste manual
    update_app()
