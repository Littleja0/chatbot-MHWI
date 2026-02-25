import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        url = 'https://monsterhunterworld.wiki.fextralife.com/Great+Sword+Comparison+Table'
        resp = await client.get(url)
        print(f"URL: {url} - Status: {resp.status_code}")
        
        # Tentar sem o "Table"
        url2 = 'https://monsterhunterworld.wiki.fextralife.com/Great+Sword+Comparison'
        resp2 = await client.get(url2)
        print(f"URL: {url2} - Status: {resp2.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
