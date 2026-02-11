import requests
import json

def find_release_asset():
    url = "https://api.github.com/repos/gatheringhallstudios/MHWorldData/releases/latest"
    print(f"Checking {url}...")
    headers = {"User-Agent": "MHW-Chatbot-Agent"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"Latest release: {data['name']}")
            for asset in data['assets']:
                print(f"Found asset: {asset['name']} - {asset['browser_download_url']}")
                if "mhw.db" in asset['name']:
                    return asset['browser_download_url']
        else:
            print(f"Failed to fetch releases: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    url = find_release_asset()
    if url:
        print(f"Downloading fro {url}...")
        r = requests.get(url, stream=True)
        with open("mhw.db", "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
