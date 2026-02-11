import os
import shutil
import stat
import subprocess
import sys
import time
import io
from pathlib import Path

# Forçar UTF-8 no stdout/stderr no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except (AttributeError, io.UnsupportedOperation):
        pass


def _force_rmtree(path):
    """Remove o diretório ignorando erros de permissão comuns no Windows."""
    def _on_error(func, fpath, exc_info):
        try:
            os.chmod(fpath, stat.S_IWRITE)
            func(fpath)
        except Exception:
            pass

    if os.path.exists(path):
        try:
            shutil.rmtree(path, onexc=_on_error)
        except Exception:
            # Técnica para Windows: Se não pode deletar, renomeia para um nome temporário
            # Isso libera o caminho original para o build continuar
            try:
                temp_path = f"{path}_old_{int(time.time())}"
                os.rename(path, temp_path)
                print(f"  📂 {path} estava travado. Renomeado para {temp_path}")
            except Exception as e:
                print(f"  ⚠️ Aviso: Não foi possível mover ou deletar {path}: {e}")

def kill_existing_process():
    """Tenta encerrar o MHWChatbot se ele estiver rodando para evitar WinError 32."""
    if sys.platform == "win32":
        try:
            print("  🔍 Verificando instâncias abertas...")
            subprocess.run(["taskkill", "/F", "/IM", "MHWChatbot.exe", "/T"], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1) # Espera o Windows liberar os arquivos
        except:
            pass


def install_pyinstaller():
    print("Checking for PyInstaller and pywebview...")
    packages = ["pyinstaller", "pywebview"]
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "show", package], stdout=subprocess.DEVNULL)
            print(f"{package} is already installed.")
        except subprocess.CalledProcessError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    # Ensure dependencies from requirements.txt are installed
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def build_frontend():
    print("Building Frontend...")
    frontend_dir = Path("frontend")
    
    # Install dependencies
    print("Installing frontend dependencies...")
    subprocess.check_call("npm install", shell=True, cwd=frontend_dir)
    
    # Build
    print("Running npm build...")
    subprocess.check_call("npm run build", shell=True, cwd=frontend_dir)

def build_exe():
    print("Building MHWChatbot...")
    
    # Clean previous builds
    _force_rmtree("build")
    _force_rmtree("dist")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",               # Oculta a janela preta do terminal
        "--onedir",                  # Mantém em pasta para ser mais rápido ao abrir
        "--name", "MHWChatbot",      # Nome do executável
        "--clean",
        "--noconfirm",
        "--add-data", f"backend/splash.html{os.pathsep}backend", # Inclui a splash
        "--add-data", f".env{os.pathsep}.",           # Inclui o .env na raiz
        "--hidden-import", "rag_pipeline",  # Pipeline de auto-atualização do RAG
        "--hidden-import", "rag_loader",    # Loader de XMLs estruturados
        "--paths", "backend",        # Adiciona a pasta backend para busca de módulos
        "backend/main.py"            # Script principal
    ]
    subprocess.check_call(cmd)
    
    # Remove temp folders if any
    _force_rmtree("build")

def copy_assets():
    print("Copying assets...")
    dist_dir = Path("dist/MHWChatbot")
    
    # Copy frontend build (dist folder from vite)
    src_frontend_dist = Path("frontend/dist")
    dst_frontend = dist_dir / "frontend"
    
    if src_frontend_dist.exists():
        _force_rmtree(dst_frontend)
        shutil.copytree(src_frontend_dist, dst_frontend)
        print(f"Frontend assets copied from {src_frontend_dist} to {dst_frontend}")
    else:
        print("Error: Frontend build not found! Run build_frontend() first.")
    
    # Copy RAG folder (XMLs)
    src_rag = Path("rag")
    dst_rag = dist_dir / "rag"
    if src_rag.exists():
        _force_rmtree(dst_rag)
        shutil.copytree(src_rag, dst_rag)
        print("RAG data (XMLs) copied to distribution.")
    
    # Copy tools (needed for updates/extraction)
    src_tools = Path("backend/game_extractor/tools")
    dst_tools = dist_dir / "game_extractor/tools"
    if src_tools.exists():
        _force_rmtree(dst_tools)
        dst_tools.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src_tools, dst_tools)
    else:
        (dist_dir / "game_extractor").mkdir(exist_ok=True)

    # Copy pre-built RAG index (storage)
    src_storage = Path("storage")
    dst_storage = dist_dir / "storage"
    if src_storage.exists():
        _force_rmtree(dst_storage)
        shutil.copytree(src_storage, dst_storage)
        print("Pre-built RAG index (storage) copied to distribution.")

if __name__ == "__main__":
    if not os.path.exists("backend/main.py"):
        print("Error: Run this script from the project root.")
        sys.exit(1)
    
    # Carregar configurações do .env
    from dotenv import load_dotenv # type: ignore
    load_dotenv()
    
    # Versão do App vinda do .env
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

    print(f"--- INICIANDO BUILD UNIFICADO (v{APP_VERSION}) ---")
    
    # 0. Limpeza de processos
    kill_existing_process()
    
    # 1. Build do Projeto
    install_pyinstaller()
    build_frontend()
    build_exe()

    # 3. Pré-indexação RAG
    print("\n--- INICIANDO PRÉ-INDEXAÇÃO RAG ---")
    try:
        sys.path.append(os.path.abspath("backend"))
        import mhw_rag
        # Garantir rebuild limpo para o build oficial
        _force_rmtree("storage")
        mhw_rag.setup_rag_engine()
        print("✓ RAG Pré-indexado com sucesso.")
    except Exception as e:
        print(f"Aviso: Falha na pré-indexação RAG: {e}")

    copy_assets()
    
    # 3. Geração do Manifesto para Auto-Update
    try:
        from build_manifest import generate_manifest # type: ignore
        generate_manifest(Path("dist/MHWChatbot"), APP_VERSION)
    except Exception as e:
        print(f"Erro ao gerar manifesto: {e}")

    print("\n" + "="*40)
    print(f"🚀 BUILD FINALIZADO COM SUCESSO (v{APP_VERSION})")
    print(f"Pasta de saída: dist/MHWChatbot")
    print("Agora é só subir o conteúdo de 'dist/MHWChatbot' para o seu Google Drive.")
    print("="*40)
