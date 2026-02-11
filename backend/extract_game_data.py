"""
Script principal para extração de dados do Monster Hunter World: Iceborne.

Este script automatiza o processo de:
1. Localizar a instalação do jogo
2. Extrair arquivos dos chunks
3. Parsear os dados do jogo
4. Gerar um banco de dados SQLite atualizado

Uso:
    python extract_game_data.py [--path CAMINHO_MHW] [--output ARQUIVO_DB]
"""

import argparse
import sys
import os
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from game_extractor.game_finder import find_mhw_installation, get_chunk_list
from game_extractor.chunk_extractor import extract_chunks, ChunkExtractor
from game_extractor.data_parser import parse_game_data
from game_extractor.db_builder import build_database


def print_header():
    """Exibe o cabeçalho do script."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║      Monster Hunter World: Iceborne - Extrator de Dados         ║
║                                                                   ║
║  Extrai dados diretamente dos arquivos do jogo para o chatbot   ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def progress_callback(message: str, progress: float):
    """Callback para exibir progresso."""
    bar_width = 30
    filled = int(bar_width * progress)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"\r[{bar}] {progress*100:5.1f}% | {message:<50}", end="", flush=True)
    if progress >= 1.0:
        print()


def check_tools():
    """Verifica se as ferramentas necessárias estão disponíveis."""
    tools_dir = Path(__file__).parent / "game_extractor" / "tools"
    tools_dir.mkdir(exist_ok=True)
    
    tool_found = False
    for tool_name in ["WorldChunkTool.exe", "MHWNoChunk.exe"]:
        tool_path = tools_dir / tool_name
        if tool_path.exists():
            print(f"✅ Ferramenta encontrada: {tool_name}")
            tool_found = True
            break
    
    if not tool_found:
        print("\n⚠️  AVISO: Nenhuma ferramenta de extração encontrada!")
        print(f"   Coloque 'WorldChunkTool.exe' ou 'MHWNoChunk.exe' em:")
        print(f"   {tools_dir}")
        print("\n   Downloads:")
        print("   - WorldChunkTool: https://github.com/mhvuze/WorldChunkTool/releases")
        print("   - MHWNoChunk: https://www.nexusmods.com/monsterhunterworld/mods/411")
        print("\n   Sem a ferramenta, a extração será limitada.")
        return False
    
    return True


def main():
    """Função principal."""
    print_header()
    
    parser = argparse.ArgumentParser(description="Extrator de dados do MHW:Iceborne")
    parser.add_argument("--path", "-p", help="Caminho para a instalação do MHW")
    parser.add_argument("--output", "-o", help="Caminho do banco de dados de saída", 
                       default="mhw.db")
    parser.add_argument("--skip-extract", action="store_true", 
                       help="Pular extração e usar dados já extraídos")
    parser.add_argument("--merge", action="store_true",
                       help="Mesclar com banco de dados existente")
    args = parser.parse_args()
    
    # PASSO 1: Localizar instalação do MHW
    print("📍 PASSO 1: Localizando Monster Hunter World...")
    print("-" * 50)
    
    if args.path:
        mhw_path = args.path
        install_info = {"path": mhw_path}
    else:
        install_info = find_mhw_installation()
    
    if not install_info:
        print("\n❌ Monster Hunter World não encontrado!")
        print("   Use --path para especificar o caminho manualmente:")
        print("   python extract_game_data.py --path \"C:/Steam/steamapps/common/Monster Hunter World\"")
        return 1
    
    mhw_path = install_info['path']
    print(f"✅ MHW encontrado em: {mhw_path}")
    
    if 'chunk_count' in install_info:
        print(f"   Chunks: {install_info['chunk_count']} ({install_info.get('total_size_gb', '?')} GB)")
        print(f"   Iceborne: {'Sim ✓' if install_info.get('has_iceborne') else 'Não'}")
    
    # Verificar ferramentas
    print()
    check_tools()
    
    # PASSO 2: Extrair chunks
    extracted_dir = Path(__file__).parent / "game_extractor" / "extracted_data"
    
    if not args.skip_extract:
        print("\n📦 PASSO 2: Extraindo arquivos do jogo...")
        print("-" * 50)
        print("   ⚠️  Este processo pode demorar vários minutos!")
        print("   ⚠️  Requer espaço em disco significativo (~10-20GB)")
        
        confirm = input("\n   Continuar com extração? (s/N): ").strip().lower()
        if confirm != 's':
            print("   Extração pulada. Usando dados existentes (se houver)...")
        else:
            success = extract_chunks(mhw_path, str(extracted_dir), progress_callback)
            if not success:
                print("\n⚠️  Extração não completada. Continuando com dados parciais...")
    else:
        print("\n📦 PASSO 2: Pulando extração (usando dados existentes)...")
    
    # PASSO 3: Parsear dados
    print("\n🔍 PASSO 3: Parseando dados do jogo...")
    print("-" * 50)
    
    parsed_data_file = extracted_dir / "parsed_data.json"
    
    if extracted_dir.exists():
        parsed_data = parse_game_data(str(extracted_dir))
        print(f"   Monstros encontrados: {len(parsed_data.get('monsters', {}))}")
        print(f"   Itens encontrados: {len(parsed_data.get('items', {}))}")
    else:
        print("   Nenhum dado extraído encontrado.")
        parsed_data = {"monsters": {}, "items": {}}
    
    # PASSO 4: Construir banco de dados
    print("\n🗄️  PASSO 4: Construindo banco de dados...")
    print("-" * 50)
    
    output_db = Path(__file__).parent / args.output
    existing_db = Path(__file__).parent / "mhw.db" if args.merge else None
    
    if parsed_data_file.exists() or (existing_db and existing_db.exists()):
        db_path = build_database(
            str(parsed_data_file) if parsed_data_file.exists() else "",
            str(output_db),
            str(existing_db) if existing_db and existing_db.exists() else None
        )
        print(f"\n✅ Banco de dados criado: {db_path}")
    else:
        print("   Sem dados para construir banco.")
        if existing_db and existing_db.exists():
            print(f"   Usando banco existente: {existing_db}")
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📋 RESUMO")
    print("=" * 50)
    print(f"   Caminho MHW: {mhw_path}")
    print(f"   Dados extraídos: {extracted_dir}")
    print(f"   Banco de dados: {output_db}")
    
    if output_db.exists():
        print(f"   Tamanho do banco: {output_db.stat().st_size / 1024 / 1024:.2f} MB")
    
    print("\n✨ Processo concluído!")
    print("   O banco de dados está pronto para uso pelo chatbot.")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
