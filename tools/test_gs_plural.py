import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        # Testar plural
        url = 'https://monsterhunterworld.wiki.fextralife.com/Great+Swords'
        resp = await client.get(url, follow_redirects=True)
        print(f"URL: {url} - Status: {resp.status_code}")
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('table', class_='wiki_table')
        print(f"Tables found: {len(tables)}")
        
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if rows:
                header = [c.get_text(strip=True) for c in rows[0].find_all(['th', 'td'])]
                print(f"Table {i} Header: {header}")
                # Sample row if exists
                if len(rows) > 1:
                     print(f"Sample: {[c.get_text(strip=True) for c in rows[1].find_all('td')]}")

if __name__ == "__main__":
    asyncio.run(main())
