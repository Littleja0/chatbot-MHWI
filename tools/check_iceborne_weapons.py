import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Iceborne+Great+Swords')
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', class_='wiki_table')
        if table:
            rows = table.find_all('tr')
            if rows:
                header = [c.get_text(strip=True) for c in rows[0].find_all(['th', 'td'])]
                print(f"Header: {header}")
                cols = rows[1].find_all('td')
                print(f"Num columns: {len(cols)}")
                print(f"Sample: {[c.get_text(strip=True) for c in cols]}")

if __name__ == "__main__":
    asyncio.run(main())
