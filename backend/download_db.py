import requests
import os

# URL da API do GitHub para obter a última release do MHWorldData
GITHUB_API_URL = "https://api.github.com/repos/gatheringhallstudios/MHWorldData/releases/latest"

# URL direta da última versão conhecida (V46 - backup)
DIRECT_DOWNLOAD_URL = "https://github.com/gatheringhallstudios/MHWorldData/releases/download/V46/mhw.db"

def get_latest_release_url():
    """Obtém a URL de download da release mais recente via API do GitHub."""
    try:
        print("Verificando última versão no GitHub...")
        r = requests.get(GITHUB_API_URL, headers={"Accept": "application/vnd.github.v3+json"})
        if r.status_code == 200:
            data = r.json()
            version = data.get("tag_name", "desconhecida")
            published = data.get("published_at", "desconhecida")
            assets = data.get("assets", [])
            
            print(f"Última versão: {version} (publicada em {published})")
            
            for asset in assets:
                if asset["name"] == "mhw.db":
                    return asset["browser_download_url"]
            print("mhw.db não encontrado nos assets da release.")
        else:
            print(f"Erro ao consultar API do GitHub: {r.status_code}")
    except Exception as e:
        print(f"Erro ao obter release: {e}")
    return None

def download_db():
    """Baixa o banco de dados mhw.db da última release."""
    # Primeiro tenta obter a URL da API
    url = get_latest_release_url()
    
    # Fallback para URL direta se a API falhar
    if not url:
        print("Usando URL de backup...")
        url = DIRECT_DOWNLOAD_URL
    
    print(f"Baixando de: {url}")
    try:
        r = requests.get(url, stream=True, allow_redirects=True)
        if r.status_code == 200:
            total_size = int(r.headers.get('content-length', 0))
            downloaded = 0
            
            with open("mhw.db", "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgresso: {percent:.1f}%", end="", flush=True)
            
            print("\nDownload completo!")
            return True
        else:
            print(f"Erro no download: {r.status_code}")
    except Exception as e:
        print(f"Erro: {e}")
    return False

if __name__ == "__main__":
    if download_db():
        print("Success!")
        # Check if it's a valid SQLite file
        try:
            import sqlite3
            conn = sqlite3.connect("mhw.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("Tables found:", [t[0] for t in tables])
            conn.close()
        except Exception as e:
            print(f"Invalid DB file: {e}")
    else:
        print("Failed to find mhw.db")
