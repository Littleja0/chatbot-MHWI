import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Great+Sword')
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('table', class_='wiki_table')
        print(f"Total tables: {len(tables)}")
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if rows:
                header = [c.get_text(strip=True) for c in rows[0].find_all(['th', 'td'])]
                print(f"Table {i} Header: {header}")
                # Check for Rarity 1-8
                sample_rarity = ""
                for row in rows[1:10]:
                    cols = row.find_all('td')
                    if len(cols) > 4:
                        sample_rarity = cols[4].get_text(strip=True)
                        break
                print(f"Sample Rarity: {sample_rarity}")

if __name__ == "__main__":
    asyncio.run(main())
