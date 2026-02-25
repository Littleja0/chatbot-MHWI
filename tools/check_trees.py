import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        urls = [
            'https://monsterhunterworld.wiki.fextralife.com/Great+Sword+Tree',
            'https://monsterhunterworld.wiki.fextralife.com/Long+Sword+Tree'
        ]
        for url in urls:
            resp = await client.get(url)
            print(f"URL: {url} - Status: {resp.status_code}")
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                tables = soup.find_all('table', class_='wiki_table')
                print(f"Found {len(tables)} tables")
                if tables:
                    rows = tables[0].find_all('tr')
                    if rows:
                        header = [c.get_text(strip=True) for c in rows[0].find_all(['th', 'td'])]
                        print(f"Header: {header}")

if __name__ == "__main__":
    asyncio.run(main())
