"""
Localiza a instalação do Monster Hunter World no sistema.
Suporta instalações via Steam e caminhos personalizados.
"""

import os
import winreg
import json
from pathlib import Path
from typing import Optional, Dict, List

# Nomes possíveis da pasta do jogo
MHW_FOLDER_NAMES = [
    "Monster Hunter World",
    "MONSTER HUNTER WORLD",
    "MonsterHunterWorld"
]

# Arquivos que confirmam ser a pasta correta do MHW
MHW_VALIDATION_FILES = [
    "MonsterHunterWorld.exe",
    "chunk/chunk0.bin",
    "chunk/chunkG0.bin"  # Iceborne
]


def find_steam_library_folders() -> List[Path]:
    """
    Encontra todas as pastas de biblioteca Steam no sistema.
    """
    libraries = []
    
    # Tenta encontrar o Steam via registro do Windows
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SOFTWARE\WOW6432Node\Valve\Steam")
        steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
        winreg.CloseKey(key)
        
        steam_path = Path(steam_path)
        if steam_path.exists():
            # Pasta principal do Steam
            steamapps = steam_path / "steamapps"
            if steamapps.exists():
                libraries.append(steamapps)
            
            # Verificar libraryfolders.vdf para pastas adicionais
            vdf_path = steamapps / "libraryfolders.vdf"
            if vdf_path.exists():
                libraries.extend(parse_library_folders_vdf(vdf_path))
                
    except (WindowsError, FileNotFoundError):
        pass
    
    # Caminhos padrão comuns
    common_paths = [
        Path("C:/Program Files (x86)/Steam/steamapps"),
        Path("C:/Program Files/Steam/steamapps"),
        Path("D:/Steam/steamapps"),
        Path("D:/SteamLibrary/steamapps"),
        Path("E:/Steam/steamapps"),
        Path("E:/SteamLibrary/steamapps"),
    ]
    
    for path in common_paths:
        if path.exists() and path not in libraries:
            libraries.append(path)
    
    return libraries


def parse_library_folders_vdf(vdf_path: Path) -> List[Path]:
    """
    Parse do arquivo libraryfolders.vdf do Steam para encontrar bibliotecas adicionais.
    """
    libraries = []
    
    try:
        with open(vdf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse simples do VDF (não é JSON, mas estrutura similar)
        import re
        # Procura por "path" seguido do caminho entre aspas
        paths = re.findall(r'"path"\s+"([^"]+)"', content)
        
        for path_str in paths:
            path = Path(path_str.replace("\\\\", "/")) / "steamapps"
            if path.exists():
                libraries.append(path)
                
    except Exception as e:
        print(f"Erro ao parsear libraryfolders.vdf: {e}")
    
    return libraries


def find_oo2core_dll(mhw_path: Path) -> Optional[str]:
    """
    Procura a DLL oo2core necessária para descompressão Oodle.
    A DLL pode estar em vários locais.
    """
    dll_names = ["oo2core_8_win64.dll", "oo2core_5_win64.dll", "oo2core_9_win64.dll"]
    
    # Locais para procurar
    search_paths = [
        mhw_path,  # Pasta principal do MHW
        mhw_path / "bin",
        Path.home() / "Downloads",
        Path(__file__).parent / "tools",
        Path("C:/Windows/System32"),
    ]
    
    # Procurar em jogos comuns que têm a DLL
    common_games = [
        "Warframe",
        "Star Wars Jedi Fallen Order", 
        "STAR WARS Jedi Survivor",
        "Cyberpunk 2077",
    ]
    
    for library in find_steam_library_folders():
        common_folder = library / "common"
        for game in common_games:
            game_path = common_folder / game
            if game_path.exists():
                search_paths.append(game_path)
    
    # Procurar
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        for dll_name in dll_names:
            dll_path = search_path / dll_name
            if dll_path.exists():
                return str(dll_path)
            
            # Procurar recursivamente (máximo 2 níveis)
            try:
                for subdir in search_path.iterdir():
                    if subdir.is_dir():
                        dll_in_subdir = subdir / dll_name
                        if dll_in_subdir.exists():
                            return str(dll_in_subdir)
            except PermissionError:
                continue
    
    return None


def validate_mhw_folder(folder: Path) -> bool:
    """
    Valida se uma pasta é realmente a instalação do MHW.
    """
    for validation_file in MHW_VALIDATION_FILES:
        if (folder / validation_file).exists():
            return True
    return False


def find_mhw_installation(custom_path: Optional[str] = None) -> Optional[Dict]:
    """
    Encontra a instalação do Monster Hunter World.
    
    Args:
        custom_path: Caminho personalizado para procurar (opcional)
    
    Returns:
        Dict com informações da instalação ou None se não encontrado
    """
    
    # Se um caminho personalizado foi fornecido
    if custom_path:
        path = Path(custom_path)
        if path.exists() and validate_mhw_folder(path):
            return get_installation_info(path)
    
    # Procurar nas bibliotecas Steam
    libraries = find_steam_library_folders()
    
    for library in libraries:
        common_folder = library / "common"
        if not common_folder.exists():
            continue
            
        for folder_name in MHW_FOLDER_NAMES:
            mhw_path = common_folder / folder_name
            if mhw_path.exists() and validate_mhw_folder(mhw_path):
                return get_installation_info(mhw_path)
    
    return None


def get_installation_info(mhw_path: Path) -> Dict:
    """
    Coleta informações sobre a instalação do MHW.
    """
    chunk_folder = mhw_path / "chunk"
    
    # Lista todos os arquivos chunk
    chunk_files = []
    if chunk_folder.exists():
        chunk_files = sorted([
            f.name for f in chunk_folder.iterdir() 
            if f.name.endswith('.bin') and f.name.startswith('chunk')
        ])
    
    # Verifica se tem Iceborne (chunkG*.bin)
    has_iceborne = any(f.startswith('chunkG') for f in chunk_files)
    
    # Verifica tamanho total dos chunks
    total_size = sum(
        (chunk_folder / f).stat().st_size 
        for f in chunk_files 
        if (chunk_folder / f).exists()
    )
    
    # Verifica oo2core DLL (necessário para descompressão)
    oo2core_dll = find_oo2core_dll(mhw_path)
    
    return {
        "path": str(mhw_path),
        "chunk_folder": str(chunk_folder),
        "chunk_files": chunk_files,
        "chunk_count": len(chunk_files),
        "total_size_gb": round(total_size / (1024**3), 2),
        "has_iceborne": has_iceborne,
        "oo2core_dll": oo2core_dll,
        "exe_path": str(mhw_path / "MonsterHunterWorld.exe")
    }


def get_chunk_list(mhw_path: str) -> List[str]:
    """
    Retorna lista ordenada de arquivos chunk para extração.
    Ordem importante: chunks base primeiro, depois Iceborne (G), depois atualizações.
    """
    chunk_folder = Path(mhw_path) / "chunk"
    if not chunk_folder.exists():
        return []
    
    chunks = []
    for f in chunk_folder.iterdir():
        if f.name.endswith('.bin') and f.name.startswith('chunk'):
            chunks.append(str(f))
    
    # Ordenar: chunk0, chunk1, ..., chunkG0, chunkG1, ...
    def chunk_sort_key(path):
        name = Path(path).stem  # chunk0, chunkG0, etc.
        if 'G' in name:
            # Iceborne chunks vêm depois
            num = name.replace('chunk', '').replace('G', '')
            return (1, int(num) if num else 0)
        else:
            num = name.replace('chunk', '')
            return (0, int(num) if num else 0)
    
    return sorted(chunks, key=chunk_sort_key)


if __name__ == "__main__":
    print("Procurando instalação do Monster Hunter World...")
    result = find_mhw_installation()
    
    if result:
        print("\n✅ MHW encontrado!")
        print(f"   Caminho: {result['path']}")
        print(f"   Chunks: {result['chunk_count']} arquivos ({result['total_size_gb']} GB)")
        print(f"   Iceborne: {'Sim' if result['has_iceborne'] else 'Não'}")
        print(f"   oo2core DLL: {'Encontrado' if result['oo2core_dll'] else 'NÃO ENCONTRADO'}")
    else:
        print("\n❌ MHW não encontrado!")
        print("   Verifique se o jogo está instalado via Steam.")
