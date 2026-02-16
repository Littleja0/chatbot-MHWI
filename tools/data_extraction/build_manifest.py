import os
import hashlib
import json
from pathlib import Path

def get_file_hash(path):
    """Calcula o SHA256 de um arquivo."""
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_manifest(root_dir, version="1.0.0"):
    """
    Gera um manifesto de todos os arquivos importantes para o update.
    Inclui: backend, frontend, rag e o executável principal.
    """
    manifest = {
        "version": version,
        "files": {}
    }
    
    # Pastas para monitorar (adicione ou remova conforme necessário)
    folders_to_include = ["backend", "frontend/dist", "rag"]
    # Arquivos individuais na raiz
    files_to_include = ["requirements.txt", "run.bat"]
    
    # Se estiver rodando após um build oficial (pasta dist/MHWChatbot)
    # podemos gerar o manifesto da pasta final de distribuição.
    dist_path = Path("dist/MHWChatbot")
    if dist_path.exists():
        print(f"Gerando manifesto a partir da pasta de distribuição: {dist_path}")
        source_root = dist_path
    else:
        print("Pasta dist/MHWChatbot não encontrada. Gerando manifesto da pasta raiz do projeto.")
        source_root = Path(".")

    for root, dirs, files in os.walk(source_root):
        # Pular pastas indesejadas
        if ".git" in dirs: dirs.remove(".git")
        if ".venv" in dirs: dirs.remove(".venv")
        if "__pycache__" in dirs: dirs.remove("__pycache__")
        if "storage" in dirs: dirs.remove("storage") # O storage do LlamaIndex é gerado localmente
        if "backups" in dirs: dirs.remove("backups")
        
        for file in files:
            file_path = Path(root) / file
            # Caminho relativo para o manifesto
            rel_path = file_path.relative_to(source_root)
            
            # Pular o próprio manifesto
            if rel_path.name == "manifest.json":
                continue
                
            manifest["files"][str(rel_path).replace("\\", "/")] = get_file_hash(file_path)

    manifest_path = source_root / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)
    
    print(f"✅ Manifesto gerado com sucesso em: {manifest_path}")
    print(f"Total de arquivos mapeados: {len(manifest['files'])}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--v", default="1.0.0", help="Versão do App")
    args = parser.parse_args()
    
    generate_manifest(".", args.v)
