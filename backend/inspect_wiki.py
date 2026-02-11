
import requests
from bs4 import BeautifulSoup

url = "https://monsterhunterworld.wiki.fextralife.com/Rimeguard+Helm+Alpha%2B"
print(f"Fetching {url}...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Print table
        tables = soup.find_all('table', class_='wiki_table')
        if tables:
            print(f"Found {len(tables)} wiki tables.")
            print(tables[0].prettify()[:2000]) # First table often contains stats
        else:
            print("No wiki_table found.")
            
        # Print slots specifically
        print("\n--- SLOTS ---")
        slots_sec = soup.find_all(string="Slots")
        for s in slots_sec:
            parent = s.parent.parent # tr?
            print(parent.prettify())
            
except Exception as e:
    print(f"Error: {e}")
