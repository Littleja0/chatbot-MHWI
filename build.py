import os
import shutil
import subprocess
import sys
from pathlib import Path

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
    if os.path.exists("build"): shutil.rmtree("build")
    if os.path.exists("dist"): shutil.rmtree("dist")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",               # Oculta a janela preta do terminal
        "--onedir",                  # Mantém em pasta para ser mais rápido ao abrir
        "--name", "MHWChatbot",      # Nome do executável
        "--clean",
        "--noconfirm",
        "--add-data", f"backend/splash.html{os.pathsep}backend", # Inclui a splash
        "backend/main.py"            # Script principal
    ]
    subprocess.check_call(cmd)
    
    # Remove temp folders if any
    try:
        if os.path.exists("build"): shutil.rmtree("build")
    except:
        pass

def copy_assets():
    print("Copying assets...")
    dist_dir = Path("dist/MHWChatbot")
    
    # Copy frontend build (dist folder from vite)
    src_frontend_dist = Path("frontend/dist")
    dst_frontend = dist_dir / "frontend"
    
    if src_frontend_dist.exists():
        if dst_frontend.exists(): shutil.rmtree(dst_frontend)
        shutil.copytree(src_frontend_dist, dst_frontend)
        print(f"Frontend assets copied from {src_frontend_dist} to {dst_frontend}")
    else:
        print("Error: Frontend build not found! Run build_frontend() first.")
    
    # Copy RAG folder (XMLs)
    src_rag = Path("rag")
    dst_rag = dist_dir / "rag"
    if src_rag.exists():
        if dst_rag.exists(): shutil.rmtree(dst_rag)
        shutil.copytree(src_rag, dst_rag)
        print("RAG data (XMLs) copied to distribution.")
    
    # Copy tools (needed for updates/extraction)
    src_tools = Path("backend/game_extractor/tools")
    dst_tools = dist_dir / "game_extractor/tools"
    if src_tools.exists():
        if dst_tools.exists(): shutil.rmtree(dst_tools)
        dst_tools.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src_tools, dst_tools)
    else:
        (dist_dir / "game_extractor").mkdir(exist_ok=True)

    # Copy pre-built RAG index (storage)
    src_storage = Path("storage")
    dst_storage = dist_dir / "storage"
    if src_storage.exists():
        if dst_storage.exists(): shutil.rmtree(dst_storage)
        shutil.copytree(src_storage, dst_storage)
        print("Pre-built RAG index (storage) copied to distribution.")

if __name__ == "__main__":
    if not os.path.exists("backend/main.py"):
        print("Error: Run this script from the project root.")
        sys.exit(1)
    
    # Versão do App
    APP_VERSION = "1.0.0"

    print(f"--- INICIANDO BUILD UNIFICADO (v{APP_VERSION}) ---")
    
    # 1. Limpeza de XMLs
    try:
        from slim_rag_xml import slim_xml_files
        slim_xml_files()
    except Exception as e:
        print(f"Aviso: Falha ao rodar limpeza de XML: {e}")

    # 2. Build do Projeto
    install_pyinstaller()
    build_frontend()
    build_exe()

    # 3. Pré-indexação RAG (Para evitar espera do usuário no primeiro boot)
    print("\n--- INICIANDO PRÉ-INDEXAÇÃO RAG ---")
    try:
        # Adicionar backend ao path para importar mhw_rag
        sys.path.append(os.path.abspath("backend"))
        import mhw_rag
        # Isso vai gerar a pasta 'storage' na raiz
        mhw_rag.setup_rag_engine()
        print("✓ RAG Pré-indexado com sucesso.")
    except Exception as e:
        print(f"Aviso: Falha na pré-indexação RAG: {e}")

    copy_assets()
    
    # 3. Geração do Manifesto para Auto-Update
    try:
        from build_manifest import generate_manifest
        generate_manifest(Path("dist/MHWChatbot"), APP_VERSION)
    except Exception as e:
        print(f"Erro ao gerar manifesto: {e}")

    print("\n" + "="*40)
    print(f"🚀 BUILD FINALIZADO COM SUCESSO (v{APP_VERSION})")
    print(f"Pasta de saída: dist/MHWChatbot")
    print("Agora é só subir o conteúdo de 'dist/MHWChatbot' para o seu Google Drive.")
    print("="*40)
