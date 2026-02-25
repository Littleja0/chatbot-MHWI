import httpx
import asyncio
from bs4 import BeautifulSoup
import re

async def main():
    async with httpx.AsyncClient() as client:
        # Página da árvore de armas
        url = 'https://monsterhunterworld.wiki.fextralife.com/Great+Sword+Weapon+Tree'
        try:
            resp = await client.get(url, follow_redirects=True)
            print(f"Checking URL: {url} - Status: {resp.status_code}")
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Tentar achar links que parecem ser armas (dentro do corpo principal)
            main_content = soup.find('div', id='wiki-content')
            if not main_content:
                main_content = soup
                
            links = main_content.find_all('a')
            
            print(f"Total links found: {len(links)}")
            
            weapon_names = []
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Filtrar links irrelevantes
                if not href or href.startswith('#') or 'fextralife' in href or 'Sim' in text:
                    continue
                    
                # Armas geralmente não têm espaços no href (usam +), mas vamos checar o texto
                if text and len(text) > 3:
                     weapon_names.append((text, href))

            print("Potential Weapons found in Tree page:")
            for name, href in weapon_names[:20]:
                print(f" - {name} ({href})")
                
        except Exception as e:
            print(f"Error accessing {url}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
