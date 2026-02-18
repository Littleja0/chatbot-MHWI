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
            # Técnica para Windows: Se não pode deletar, renomeia
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
    
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def build_frontend():
    print("Building Frontend...")
    frontend_dir = Path("apps/frontend")
    
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

    # Define paths
    backend_src = "apps/backend/src"
    main_script = f"{backend_src}/main.py"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",               # Oculta a janela preta do terminal
        "--onedir",                  # Mantém em pasta para ser mais rápido ao abrir
        "--name", "MHWChatbot",      # Nome do executável
        "--clean",
        "--noconfirm",
        "--add-data", f"{backend_src}/templates/splash.html{os.pathsep}apps/backend/src/templates", # Inclui a splash
        "--add-data", f".env{os.pathsep}.",           # Inclui o .env na raiz
        "--hidden-import", "core.mhw.rag_pipeline",  # Pipeline de auto-atualização do RAG
        "--hidden-import", "core.mhw.rag_loader",    # Loader de XMLs estruturados
        "--paths", backend_src,      # Adiciona a pasta src para busca de módulos
        main_script                  # Script principal
    ]
    subprocess.check_call(cmd)
    
    # Remove temp folders if any
    _force_rmtree("build")

def copy_assets():
    print("Copying assets...")
    dist_dir = Path("dist/MHWChatbot")
    
    # Copy frontend build (dist folder from vite)
    # The frontend writes to dist/MHWChatbot/frontend/dist so main.py can find it relative to app root?
    # backend/src/main.py uses:
    # frontend_dist = os.path.join(_apps_dir, "frontend", "dist")
    # If using PyInstaller onedir, we are at dist/MHWChatbot.
    # We should place frontend at dist/MHWChatbot/apps/frontend/dist TO MATCH main.py logic?
    # Or rely on fallback logic if main.py has it.
    # main.py fallbacks: 
    #   frontend_dist = os.path.join(_root, "frontend", "dist")
    # Let's create 'frontend/dist' in the root of the EXE folder, and ensure main.py finds it.
    # But main.py checks `_apps_dir` which is `.../backend` -> parent -> parent.
    # In PyInstaller, `__file__` is in `_internal/.../main.py`?
    # Wait, check `main.py` frozen logic:
    # if getattr(sys, 'frozen', False):
    #    BASE_DIR = sys._MEIPASS (onefile) or dirname(sys.executable) ?
    #    No, main.py checks:
    #    _this_dir = os.path.dirname(os.path.abspath(__file__))
    #    In ONEDIR, main.py is bytecompiled inside _internal usually? Or plain?
    #    Usually we want to keep it simple.
    
    # Let's copy to dist/MHWChatbot/apps/frontend/dist to mirror the structure expected by main.py
    # main.py: _apps_dir = parent(parent(_this_dir)) = apps
    # So if main.py is at: dist/MHWChatbot/_internal/apps/backend/src/main.py
    # Then _apps_dir is dist/MHWChatbot/_internal/apps
    # And it looks for dist/MHWChatbot/_internal/apps/frontend/dist
    # BUT we cannot easily put files into _internal.
    
    # Alternative: main.py uses ROOT_DIR fallback?
    # frontend_dist = os.path.join(_root_dir, "frontend", "dist")
    # Let's put it at dist/MHWChatbot/frontend/dist
    # And assume _root_dir points to dist/MHWChatbot.
    
    src_frontend_dist = Path("apps/frontend/dist")
    dst_frontend = dist_dir / "frontend/dist"
    
    if src_frontend_dist.exists():
        if dst_frontend.exists(): _force_rmtree(dst_frontend)
        dst_frontend.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src_frontend_dist, dst_frontend)
        print(f"Frontend assets copied to {dst_frontend}")
    else:
        print("Error: Frontend build not found! Run build_frontend() first.")
    
    # Copy Data
    src_data_dir = Path("apps/backend/src/data")
    dst_data_dir = dist_dir / "data"
    
    dst_data_dir.mkdir(exist_ok=True)
    
    # RAG
    if (src_data_dir / "rag").exists():
        if (dst_data_dir / "rag").exists(): shutil.rmtree(dst_data_dir / "rag")
        shutil.copytree(src_data_dir / "rag", dst_data_dir / "rag")
        print("RAG data copied.")
            
    # Storage
    if (src_data_dir / "storage").exists():
        if (dst_data_dir / "storage").exists(): shutil.rmtree(dst_data_dir / "storage")
        shutil.copytree(src_data_dir / "storage", dst_data_dir / "storage")
        print("Storage copied.")
            
    # DBs
    if (src_data_dir / "mhw.db").exists():
         shutil.copy2(src_data_dir / "mhw.db", dst_data_dir / "mhw.db")
         print("DB copied.")
             
    # Tools
    src_tools = Path("apps/backend/src/core/mhw/game_extractor/tools")
    dst_tools = dist_dir / "game_extractor/tools"
    if src_tools.exists():
        if dst_tools.exists(): shutil.rmtree(dst_tools)
        dst_tools.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src_tools, dst_tools)
        print("Tools copied.")

if __name__ == "__main__":
    if not os.path.exists("apps/backend/src/main.py"):
        print("Error: Run this script from the project root and ensure apps structure exists.")
        sys.exit(1)
    
    from dotenv import load_dotenv # type: ignore
    load_dotenv()
    
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

    print(f"--- INICIANDO BUILD UNIFICADO (v{APP_VERSION}) ---")
    
    kill_existing_process()
    install_pyinstaller()
    build_frontend()
    build_exe()

    print("\n--- INICIANDO PRÉ-INDEXAÇÃO RAG ---")
    try:
        sys.path.append(os.path.abspath("apps/backend/src"))
        from core.mhw import mhw_rag
        
        # Garantir rebuild limpo
        storage_path = Path("apps/backend/src/data/storage")
        _force_rmtree(storage_path)
        
        mhw_rag.setup_rag_engine()
        print("✓ RAG Pré-indexado com sucesso.")
    except Exception as e:
        print(f"Aviso: Falha na pré-indexação RAG: {e}")

    copy_assets()
    
    try:
        if os.path.exists("build_manifest.py"):
            from build_manifest import generate_manifest # type: ignore
            generate_manifest(Path("dist/MHWChatbot"), APP_VERSION)
    except Exception as e:
        print(f"Erro ao gerar manifesto: {e}")

    print("\n" + "="*40)
    print(f"🚀 BUILD FINALIZADO COM SUCESSO (v{APP_VERSION})")
    print(f"Pasta de saída: dist/MHWChatbot")
    print("="*40)
