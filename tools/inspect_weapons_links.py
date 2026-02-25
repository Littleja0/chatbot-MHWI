import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Weapons')
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Tentar achar a lista de tipos de armas
        links = soup.find_all('a', class_='wiki_link')
        print("Possible weapon type links:")
        for l in links[:50]:
            text = l.get_text(strip=True)
            href = l.get('href', '')
            if text in ["Great Sword", "Long Sword", "Dual Blades", "Hammer"]:
                print(f" - {text}: {href}")

if __name__ == "__main__":
    asyncio.run(main())
