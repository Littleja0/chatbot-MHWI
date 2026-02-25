import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        url = 'https://monsterhunterworld.wiki.fextralife.com/Great+Sword'
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        tables = soup.find_all('table', class_='wiki_table')
        
        # Focar na Tabela 2 e 3 se existirem
        for i in [2, 3]:
            if i < len(tables):
                print(f"\n--- Table {i} ---")
                table = tables[i]
                rows = table.find_all('tr')
                if rows:
                    # Header
                    print(f"Header: {[c.get_text(strip=True) for c in rows[0].find_all(['th', 'td'])]}")
                    
                    # Conteúdo da primeira linha de dados
                    if len(rows) > 1:
                        cols = rows[1].find_all('td')
                        print(f"Row 1 (cols): {[c.get_text(strip=True) for c in cols]}")
                        
                        # Se tiver links, listar alguns
                        links = rows[1].find_all('a')
                        if links:
                            print(f"Links found in Row 1: {[l.get_text(strip=True) for l in links[:5]]}")

if __name__ == "__main__":
    asyncio.run(main())
