import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Weapon+Tree')
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Procurar links para árvores específicas
        links = [a.get('href') for a in soup.find_all('a') if 'Tree' in a.get('href', '')]
        print("Tree Links:")
        for l in links[:10]:
            print(f" - {l}")

if __name__ == "__main__":
    asyncio.run(main())
