import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Great+Sword')
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a') if a.get('href')]
        print("Links on Great Sword page:")
        for l in links:
            if 'Sword' in l or 'Great' in l:
                print(f" - {l}")

if __name__ == "__main__":
    asyncio.run(main())
