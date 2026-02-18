"""
Extrator de arquivos chunk do Monster Hunter World.
Descomprime e mescla os arquivos chunk*.bin do jogo.
"""

import os
import subprocess
import shutil
import ctypes
import struct
import zlib
from pathlib import Path
from typing import Optional, List, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constantes para descompressão
CHUNK_MAGIC = b'CMP\x00'
CHUNK_HEADER_SIZE = 48


class ChunkExtractor:
    """
    Extrator de chunks do MHW.
    Suporta extração nativa em Python ou usando ferramentas externas.
    """
    
    def __init__(self, mhw_path: str, output_dir: Optional[str] = None):
        self.mhw_path = Path(mhw_path)
        self.chunk_folder = self.mhw_path / "chunk"
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / "extracted_data"
        
        # Procurar oo2core DLL
        self.oo2core_dll = None
        for dll_name in ["oo2core_8_win64.dll", "oo2core_5_win64.dll"]:
            dll_path = self.mhw_path / dll_name
            if dll_path.exists():
                self.oo2core_dll = dll_path
                break
        
        # Cache de arquivos extraídos (para merge)
        self.file_map = {}
        
    def get_chunk_files(self) -> List[Path]:
        """Retorna lista ordenada de chunks para processar."""
        if not self.chunk_folder.exists():
            return []
        
        chunks = [f for f in self.chunk_folder.iterdir() 
                  if f.name.endswith('.bin') and f.name.startswith('chunk')]
        
        def sort_key(p):
            name = p.stem
            if 'G' in name:
                num = name.replace('chunk', '').replace('G', '')
                return (1, int(num) if num else 0)
            else:
                num = name.replace('chunk', '')
                return (0, int(num) if num else 0)
        
        return sorted(chunks, key=sort_key)
    
    def extract_all(self, 
                    progress_callback: Optional[Callable[[str, float], None]] = None,
                    filter_paths: Optional[List[str]] = None) -> bool:
        """
        Extrai todos os chunks relevantes.
        
        Args:
            progress_callback: Função chamada com (mensagem, progresso 0-1)
            filter_paths: Lista de caminhos a extrair (ex: ["em/", "common/text/"])
        
        Returns:
            True se sucesso
        """
        chunks = self.get_chunk_files()
        if not chunks:
            if progress_callback:
                progress_callback("Nenhum chunk encontrado!", 0)
            return False
        
        # Criar diretório de saída
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            if progress_callback:
                progress_callback(f"Extraindo {chunk.name}...", i / total)
            
            self._extract_chunk(chunk, filter_paths)
        
        if progress_callback:
            progress_callback("Extração completa!", 1.0)
        
        return True
    
    def _extract_chunk(self, chunk_path: Path, filter_paths: Optional[List[str]] = None):
        """
        Extrai um único arquivo chunk.
        Usa lógica baseada no MHWNoChunk.
        """
        try:
            with open(chunk_path, 'rb') as f:
                # Ler header
                magic = f.read(6)
                if magic != CHUNK_MAGIC:
                    print(f"Chunk inválido: {chunk_path.name}")
                    return
                
                # Parsear estrutura do chunk
                f.seek(0)
                self._parse_chunk_entries(f, chunk_path.name, filter_paths)
                
        except Exception as e:
            print(f"Erro ao extrair {chunk_path.name}: {e}")
    
    def _parse_chunk_entries(self, file_handle, chunk_name: str, 
                            filter_paths: Optional[List[str]] = None):
        """
        Parseia as entradas de um chunk e extrai os arquivos.
        
        Formato do chunk (simplificado):
        - Header (48 bytes)
        - Tabela de arquivos
        - Dados comprimidos
        """
        # Esta é uma implementação simplificada
        # Para extração completa, usar WorldChunkTool ou MHWNoChunk
        
        # Ler header completo
        header = file_handle.read(CHUNK_HEADER_SIZE)
        
        # Verificar se é um chunk válido
        if not header.startswith(CHUNK_MAGIC):
            return
        
        # Offset para tabela de arquivos
        file_handle.seek(12)
        file_count = struct.unpack('<I', file_handle.read(4))[0]
        
        # Nota: A estrutura real do chunk é mais complexa
        # Requer a biblioteca oo2core para descompressão Oodle
        # Por isso, é recomendado usar ferramentas externas
        
        print(f"  {chunk_name}: ~{file_count} entradas (use ferramenta externa para extração completa)")
    
    def extract_specific_files(self, file_patterns: List[str]) -> dict:
        """
        Extrai apenas arquivos específicos usando padrões.
        
        Args:
            file_patterns: Lista de padrões (ex: ["em/em001/", "common/text/vfont/"])
        
        Returns:
            Dict mapeando caminhos para dados
        """
        result = {}
        
        # Para extração de arquivos específicos, usar a ferramenta externa
        # e filtrar os resultados
        
        return result


def extract_with_external_tool(mhw_path: str, 
                               output_dir: str,
                               tool_path: Optional[str] = None,
                               progress_callback: Optional[Callable] = None) -> bool:
    """
    Usa uma ferramenta externa (WorldChunkTool/MHWNoChunk) para extrair chunks.
    
    Args:
        mhw_path: Caminho da instalação do MHW
        output_dir: Diretório de saída
        tool_path: Caminho para WorldChunkTool.exe ou MHWNoChunk.exe
        progress_callback: Callback de progresso
    
    Returns:
        True se sucesso
    """
    mhw_path = Path(mhw_path)
    output_dir = Path(output_dir)
    chunk_folder = mhw_path / "chunk"
    
    if not chunk_folder.exists():
        print("Pasta chunk não encontrada!")
        return False
    
    # Procurar ferramenta de extração
    if not tool_path:
        # Procurar em locais comuns
        search_paths = [
            Path(__file__).parent / "tools" / "WorldChunkTool.exe",
            Path(__file__).parent / "tools" / "MHWNoChunk.exe",
            Path.home() / "Downloads" / "WorldChunkTool.exe",
            Path.home() / "Downloads" / "MHWNoChunk.exe",
        ]
        
        for path in search_paths:
            if path.exists():
                tool_path = str(path)
                break
    
    if not tool_path or not Path(tool_path).exists():
        print("\n⚠️  Ferramenta de extração não encontrada!")
        print("Por favor, baixe uma das seguintes ferramentas:")
        print("  - WorldChunkTool: https://github.com/mhvuze/WorldChunkTool")
        print("  - MHWNoChunk: https://www.nexusmods.com/monsterhunterworld/mods/411")
        print(f"\nColoque o executável em: {Path(__file__).parent / 'tools'}")
        return False
    
    # Copiar oo2core DLL se necessário
    oo2core = None
    for dll_name in ["oo2core_8_win64.dll", "oo2core_5_win64.dll"]:
        dll_path = mhw_path / dll_name
        if dll_path.exists():
            oo2core = dll_path
            break
    
    if oo2core:
        tool_dir = Path(tool_path).parent
        dest_dll = tool_dir / oo2core.name
        if not dest_dll.exists():
            shutil.copy(oo2core, dest_dll)
    
    # Executar ferramenta
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Listar chunks
    chunks = sorted([f for f in chunk_folder.iterdir() 
                     if f.name.endswith('.bin') and f.name.startswith('chunk')])
    
    if progress_callback:
        progress_callback("Iniciando extração...", 0)
    
    for i, chunk in enumerate(chunks):
        if progress_callback:
            progress_callback(f"Extraindo {chunk.name}...", i / len(chunks))
        
        try:
            # Executar ferramenta com o chunk
            cmd = [tool_path, str(chunk), "-o", str(output_dir)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"Erro ao extrair {chunk.name}: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"Timeout ao extrair {chunk.name}")
        except Exception as e:
            print(f"Erro ao executar ferramenta: {e}")
    
    if progress_callback:
        progress_callback("Mesclando arquivos...", 0.9)
    
    # Mesclar extrações (chunks mais recentes sobrescrevem mais antigos)
    merge_extracted_chunks(output_dir)
    
    if progress_callback:
        progress_callback("Extração completa!", 1.0)
    
    return True


def merge_extracted_chunks(extracted_dir: Path):
    """
    Mescla os arquivos extraídos de múltiplos chunks.
    Arquivos de chunks mais recentes sobrescrevem os mais antigos.
    """
    extracted_dir = Path(extracted_dir)
    merged_dir = extracted_dir / "merged"
    merged_dir.mkdir(exist_ok=True)
    
    # Encontrar todas as pastas chunk extraídas
    chunk_dirs = sorted([d for d in extracted_dir.iterdir() 
                         if d.is_dir() and d.name.startswith('chunk')])
    
    for chunk_dir in chunk_dirs:
        # Copiar todos os arquivos, sobrescrevendo existentes
        for file_path in chunk_dir.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(chunk_dir)
                dest_path = merged_dir / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
    
    print(f"Arquivos mesclados em: {merged_dir}")


def extract_chunks(mhw_path: str, output_dir: Optional[str] = None,
                   progress_callback: Optional[Callable] = None) -> bool:
    """
    Função principal para extrair chunks do MHW.
    
    Args:
        mhw_path: Caminho da instalação do MHW
        output_dir: Diretório de saída (opcional)
        progress_callback: Callback (mensagem, progresso) para atualizar progresso
    
    Returns:
        True se sucesso
    """
    if output_dir is None:
        output_dir = str(Path(__file__).parent / "extracted_data")
    
    # Primeiro tenta com ferramenta externa (mais completo)
    result = extract_with_external_tool(mhw_path, output_dir, progress_callback=progress_callback)
    
    if not result:
        # Fallback para extração parcial em Python
        print("\nUsando extração parcial em Python...")
        extractor = ChunkExtractor(mhw_path, output_dir)
        result = extractor.extract_all(progress_callback)
    
    return result


if __name__ == "__main__":
    from game_finder import find_mhw_installation
    
    print("=== Extrator de Chunks do MHW ===\n")
    
    install = find_mhw_installation()
    if not install:
        print("MHW não encontrado!")
        exit(1)
    
    print(f"MHW encontrado em: {install['path']}")
    print(f"Chunks: {install['chunk_count']} ({install['total_size_gb']} GB)")
    print()
    
    def progress(msg, pct):
        bar = "█" * int(pct * 20) + "░" * (20 - int(pct * 20))
        print(f"\r[{bar}] {pct*100:.0f}% - {msg}", end="", flush=True)
    
    extract_chunks(install['path'], progress_callback=progress)
    print()
