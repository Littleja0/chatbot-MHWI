import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Great+Sword')
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = soup.find_all('a', class_='wiki_link')
        print("Wiki links on Great Sword page:")
        for l in links:
            href = l.get('href', '')
            text = l.get_text(strip=True)
            if 'Sword' in text or 'Great' in text:
                print(f" - {text}: {href}")

if __name__ == "__main__":
    asyncio.run(main())
