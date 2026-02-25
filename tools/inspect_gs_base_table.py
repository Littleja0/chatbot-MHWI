import httpx
import asyncio
from bs4 import BeautifulSoup
import re

async def main():
    async with httpx.AsyncClient() as client:
        # Página principal da Great Sword, que deve conter armas do jogo base
        url = 'https://monsterhunterworld.wiki.fextralife.com/Great+Sword'
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        tables = soup.find_all('table', class_='wiki_table')
        print(f"URL: {url}")
        print(f"Total tables: {len(tables)}")
        
        # Inspecionar a Tabela 1 (índice 1, pois a 0 costuma ser infobox)
        if len(tables) > 1:
            table = tables[1]
            rows = table.find_all('tr')
            if rows:
                header = [c.get_text(strip=True) for c in rows[0].find_all(['th', 'td'])]
                print(f"Table 1 Header: {header}")
                
                print("\nSample Rows:")
                count_lr_hr = 0
                count_mr = 0
                
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 5:
                        name = cols[0].get_text(strip=True)
                        rarity_text = cols[4].get_text(strip=True)
                        
                        # Tentar extrair número da raridade
                        try:
                            rarity = int(re.search(r'\d+', rarity_text).group())
                            if rarity < 9:
                                count_lr_hr += 1
                                if count_lr_hr <= 5: # Mostrar os primeiros 5 encontrados
                                    print(f"  [LR/HR] Name: {name}, Rarity: {rarity}")
                            else:
                                count_mr += 1
                        except:
                            pass
                
                print(f"\nStats: LR/HR (Rare < 9): {count_lr_hr}, MR (Rare >= 9): {count_mr}")

if __name__ == "__main__":
    asyncio.run(main())
