import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Weapons')
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a') if a.get('href')]
        comparison_links = [l for l in links if 'Comparison' in l]
        print("Comparison Links found:")
        for l in comparison_links:
            print(f" - {l}")

if __name__ == "__main__":
    asyncio.run(main())
