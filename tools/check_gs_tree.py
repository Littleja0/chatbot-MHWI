import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        url = 'https://monsterhunterworld.wiki.fextralife.com/Great+Sword+Weapon+Tree'
        resp = await client.get(url, follow_redirects=True)
        print(f"URL: {url} - Final URL: {resp.url} - Status: {resp.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
