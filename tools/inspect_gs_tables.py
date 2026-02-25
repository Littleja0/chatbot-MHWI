import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Great+Sword')
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('table', class_='wiki_table')
        for i, table in enumerate(tables):
            print(f"\n--- Table {i} ---")
            rows = table.find_all('tr')
            if rows:
                print(f"Header: {[c.get_text(strip=True) for c in rows[0].find_all(['th', 'td'])]}")
                if len(rows) > 1:
                    print(f"Sample Row: {[c.get_text(strip=True) for c in rows[1].find_all('td')]}")

if __name__ == "__main__":
    asyncio.run(main())
