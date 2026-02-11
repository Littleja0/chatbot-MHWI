"""
Sistema de atualização automática do banco de dados MHW.
Baixa ferramentas, extrai dados e atualiza o banco de forma totalmente automática.
"""

import os
import sys
import shutil
import zipfile
import requests  # type: ignore
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Diretórios
if getattr(sys, 'frozen', False):
    # Se estiver rodando como executável (PyInstaller)
    BACKEND_DIR = Path(sys.executable).parent
else:
    # Se estiver rodando como script normal
    BACKEND_DIR = Path(__file__).parent
TOOLS_DIR = BACKEND_DIR / "game_extractor" / "tools"
EXTRACTED_DIR = BACKEND_DIR / "game_extractor" / "extracted_data"
DB_PATH = BACKEND_DIR / "mhw.db"

# URLs
GITHUB_RELEASES_API = "https://api.github.com/repos/gatheringhallstudios/MHWorldData/releases/latest"
WORLDCHUNKTOOL_URL = "https://github.com/mhvuze/WorldChunkTool/releases/download/1.2.2/WorldChunkTool.exe"

# Configurações
AUTO_UPDATE_INTERVAL_DAYS = 7  # Verificar atualização a cada X dias


def log(msg: str):
    """Loga mensagem com timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")


def check_db_age() -> int:
    """Retorna idade do banco de dados em dias."""
    if not DB_PATH.exists():
        return 999  # Forçar atualização
    
    mtime = datetime.fromtimestamp(DB_PATH.stat().st_mtime)
    age = datetime.now() - mtime
    return age.days


def download_latest_db() -> bool:
    """
    Baixa a versão mais recente do banco de dados do GitHub.
    """
    log("Verificando última versão do banco de dados...")
    
    try:
        # Consultar API do GitHub
        r = requests.get(GITHUB_RELEASES_API, headers={"Accept": "application/vnd.github.v3+json"}, timeout=10)
        
        if r.status_code != 200:
            log(f"Erro ao consultar GitHub: {r.status_code}")
            return False
        
        data = r.json()
        version = data.get("tag_name", "?")
        published = data.get("published_at", "?")[:10]
        
        # Encontrar asset mhw.db
        download_url = None
        for asset in data.get("assets", []):
            if asset["name"] == "mhw.db":
                download_url = asset["browser_download_url"]
                break
        
        if not download_url:
            log("mhw.db não encontrado na release")
            return False
        
        log(f"Versão disponível: {version} ({published})")
        
        # Verificar se já temos esta versão
        version_file = BACKEND_DIR / ".db_version"
        if version_file.exists():
            current_version = version_file.read_text().strip()
            if current_version == version:
                log("Banco de dados já está atualizado!")
                return True
        
        # Baixar
        log("Baixando banco de dados...")
        r = requests.get(download_url, stream=True, timeout=60)
        
        if r.status_code == 200:
            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            
            # Backup do banco atual
            if DB_PATH.exists():
                backup = DB_PATH.with_suffix('.db.backup')
                shutil.copy(DB_PATH, backup)
            
            with open(DB_PATH, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)  # type: ignore
                    downloaded += len(chunk)
                    if total > 0:
                        pct = (downloaded / total) * 100
                        print(f"\r   Progresso: {pct:.0f}%", end="", flush=True)
            
            print()
            
            # Salvar versão
            version_file.write_text(version)
            
            log(f"✅ Banco atualizado para versão {version}")
            return True
        else:
            log(f"Erro no download: {r.status_code}")
            return False
            
    except requests.Timeout:
        log("Timeout ao conectar com GitHub")
        return False
    except Exception as e:
        log(f"Erro: {e}")
        return False


def download_extraction_tool() -> bool:
    """
    Baixa WorldChunkTool automaticamente se não existir.
    """
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    tool_exe = TOOLS_DIR / "WorldChunkTool.exe"
    
    if tool_exe.exists():
        return True
    
    log("Baixando ferramenta de extração (WorldChunkTool)...")
    
    try:
        r = requests.get(WORLDCHUNKTOOL_URL, stream=True, timeout=60)
        
        if r.status_code == 200:
            if WORLDCHUNKTOOL_URL.endswith('.zip'):
                zip_path = TOOLS_DIR / "WorldChunkTool.zip"
                with open(zip_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                with zipfile.ZipFile(zip_path, 'r') as z:
                    z.extractall(TOOLS_DIR)
                zip_path.unlink()
            else:
                # Direct EXE download
                with open(tool_exe, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            if tool_exe.exists():
                log("✅ WorldChunkTool instalado!")
                return True
            else:
                # Procurar em subpastas caso tenha sido extraído de um ZIP
                for f in TOOLS_DIR.rglob("WorldChunkTool.exe"):
                    if f != tool_exe:
                        shutil.move(str(f), str(tool_exe))
                        return True
                
        log(f"Erro ao baixar ferramenta: status {r.status_code}")
        return False
        
    except Exception as e:
        log(f"Erro ao baixar ferramenta: {e}")
        return False


def should_update() -> bool:
    """
    Verifica se deve atualizar o banco de dados.
    """
    # Se não existe, atualizar
    if not DB_PATH.exists():
        return True
    
    # Verificar idade
    age = check_db_age()
    if age >= AUTO_UPDATE_INTERVAL_DAYS:
        log(f"Banco de dados tem {age} dias, verificando atualizações...")
        return True
    
    return False


def quick_update():
    """
    Atualização rápida - apenas baixa do GitHub se necessário.
    Executada automaticamente no startup.
    """
    if not should_update():
        log("Banco de dados OK")
        return True
    
    return download_latest_db()


def full_update(mhw_path: Optional[str] = None):
    """
    Atualização completa - extrai dados do jogo instalado.
    Requer MHW instalado e ferramenta de extração.
    """
    # Importar módulos de extração
    sys.path.insert(0, str(BACKEND_DIR))
    
    from game_extractor.game_finder import find_mhw_installation  # type: ignore
    from game_extractor.chunk_extractor import extract_chunks  # type: ignore
    from game_extractor.data_parser import parse_game_data  # type: ignore
    from game_extractor.db_builder import build_database  # type: ignore
    
    log("=== Atualização Completa do Banco de Dados ===")
    
    # Encontrar MHW
    if mhw_path:
        install = {"path": mhw_path}
    else:
        install = find_mhw_installation()
    
    if not install:
        log("❌ MHW não encontrado! Usando banco do GitHub...")
        return download_latest_db()
    
    log(f"MHW encontrado: {install['path']}")
    
    # Baixar ferramenta se necessário
    if not download_extraction_tool():
        log("⚠️ Sem ferramenta de extração, usando banco do GitHub...")
        return download_latest_db()
    
    # Extrair chunks
    log("Extraindo dados do jogo (isso pode demorar)...")
    
    def progress(msg, pct):
        print(f"\r   [{int(pct*100):3d}%] {msg[:50]:<50}", end="", flush=True)
    
    try:
        success = extract_chunks(install['path'], str(EXTRACTED_DIR), progress)
        print()
        
        if not success:
            log("⚠️ Extração parcial, usando banco do GitHub como base...")
            download_latest_db()
    except Exception as e:
        log(f"Erro na extração: {e}")
        return download_latest_db()
    
    # Parsear dados
    log("Parseando dados...")
    parsed_file = EXTRACTED_DIR / "parsed_data.json"
    
    if EXTRACTED_DIR.exists():
        try:
            parse_game_data(str(EXTRACTED_DIR))
        except Exception as e:
            log(f"Erro no parsing: {e}")
    
    # Construir banco
    log("Construindo banco de dados...")
    try:
        build_database(
            str(parsed_file) if parsed_file.exists() else "",
            str(DB_PATH),
            str(DB_PATH) if DB_PATH.exists() else None
        )
        # Sanitizar banco de dados após a construção
        try:
            from . import sanitize_db
            sanitize_db.sanitize_armor_slots(str(DB_PATH))
        except ImportError:
            import sanitize_db
            sanitize_db.sanitize_armor_slots(str(DB_PATH))
            
        log("✅ Banco de dados atualizado e sanitizado!")
        return True
    except Exception as e:
        log(f"Erro ao construir banco: {e}")
        return download_latest_db()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Atualizador de banco de dados MHW")
    parser.add_argument("--full", action="store_true", help="Extração completa do jogo")
    parser.add_argument("--force", action="store_true", help="Forçar atualização")
    parser.add_argument("--path", help="Caminho do MHW")
    args = parser.parse_args()
    
    if args.force:
        # Remover arquivo de versão para forçar verificação
        version_file = BACKEND_DIR / ".db_version"
        if version_file.exists():
            version_file.unlink()
        # Forçar download direto
        success = download_latest_db()
    elif args.full:
        success = full_update(args.path)
    else:
        success = quick_update()
    
    sys.exit(0 if success else 1)

