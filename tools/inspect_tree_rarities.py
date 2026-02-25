import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Great+Sword+Weapon+Tree')
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('table', class_='wiki_table')
        print(f"Total tables: {len(tables)}")
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if rows:
                header = [c.get_text(strip=True) for c in rows[0].find_all(['th', 'td'])]
                print(f"\nTable {i} Header: {header}")
                # Check for Rarity 1-8
                rarities = set()
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) > 2: # Usually Tree table has Name, Attack, etc but the columns vary
                        # Looking for rarity number
                        text = row.get_text()
                        match = re.search(r'Rare\s*(\d+)', text)
                        if match: rarities.add(match.group(1))
                print(f"Rarities found: {sorted(list(rarities))}")

import re
if __name__ == "__main__":
    asyncio.run(main())
