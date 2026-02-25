import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Great+Sword')
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Procurar tabelas com armas
        tables = soup.find_all('table', class_='wiki_table')
        print(f"Found {len(tables)} tables")
        if tables:
            first_rows = tables[0].find_all('tr')[:5]
            for r in first_rows:
                print(r.get_text(strip=True))

if __name__ == "__main__":
    asyncio.run(main())
