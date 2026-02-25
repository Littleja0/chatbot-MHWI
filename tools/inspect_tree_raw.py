import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Great+Sword+Weapon+Tree')
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Tentar achar qualquer tabela
        tables = soup.find_all('table')
        print(f"Total tables: {len(tables)}")
        for i, table in enumerate(tables[:3]):
            rows = table.find_all('tr')
            if rows:
                print(f"Table {i} rows: {len(rows)}")
                print(f"First row text: {rows[0].get_text(strip=True)[:100]}")

if __name__ == "__main__":
    asyncio.run(main())
