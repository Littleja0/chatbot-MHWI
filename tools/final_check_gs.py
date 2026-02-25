import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        url = 'https://monsterhunterworld.wiki.fextralife.com/Great+Sword'
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Procurar qualquer tabela e imprimir as primeiras linhas
        tables = soup.find_all('table')
        print(f"Total Tables found: {len(tables)}")
        
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if rows:
                print(f"Table {i} Row Count: {len(rows)}")
                print(f"Header/First Row: {rows[0].get_text(strip=True)[:50]}")

if __name__ == "__main__":
    asyncio.run(main())
