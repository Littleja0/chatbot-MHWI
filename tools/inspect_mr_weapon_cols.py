import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://monsterhunterworld.wiki.fextralife.com/Iceborne+Great+Swords')
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', class_='wiki_table')
        if table:
            rows = table.find_all('tr')
            if len(rows) > 1:
                # Header
                header_cols = rows[0].find_all(['th', 'td'])
                print(f"Header ({len(header_cols)}): {[c.get_text(strip=True) for c in header_cols]}")
                
                # First Data Row
                data_row = rows[1]
                cols = data_row.find_all('td')
                print(f"Data Row ({len(cols)}):")
                for i, c in enumerate(cols):
                    print(f"  Col {i}: {c.get_text(strip=True)}")
                    # Check for slots in this column
                    if 'gem' in str(c) or 'slot' in str(c):
                        print(f"    -> Potential Slot info here: {c}")

if __name__ == "__main__":
    asyncio.run(main())
