import httpx
import asyncio
from bs4 import BeautifulSoup
import os
import hashlib
from pathlib import Path
import json
import re

# Configuração de Cache
CACHE_DIR = Path("data/cache/wiki")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class WikiScraper:
    """
    Scraper central para coletar dados da Wiki Fextralife de MHW:I.
    Focado em performance (httpx) e qualidade (BeautifulSoup4).
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.client = httpx.AsyncClient(timeout=30.0, headers=self.headers)

    async def fetch(self, url: str, retries: int = 3) -> str:
        """
        Obtém o conteúdo HTML de uma URL com sistema de cache local e retentativas.
        """
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_path = CACHE_DIR / f"{url_hash}.html"

        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8")

        for i in range(retries):
            print(f"📡 Buscando (remoto - tentativa {i+1}): {url}")
            try:
                resp = await self.client.get(url, follow_redirects=True)
                resp.raise_for_status()
                html = resp.text
                
                # Salvar no cache
                cache_path.write_text(html, encoding="utf-8")
                
                # Delay de cortesia para evitar bloqueios
                await asyncio.sleep(1.5)
                return html
            except Exception as e:
                if i == retries - 1:
                    print(f"❌ Erro final ao buscar {url}: {e}")
                else:
                    wait_time = 2 * (i + 1)
                    print(f"⚠️ Erro ao buscar {url} ({e}). Tentando novamente em {wait_time}s...")
                    await asyncio.sleep(wait_time)
        return ""

    async def close(self):
        await self.client.aclose()

    def parse_slots(self, cell: BeautifulSoup) -> list[int]:
        """Extrai níveis de slots de uma célula da tabela."""
        slots = []
        for img in cell.find_all("img"):
            src = img.get("src", "").lower()
            if "gem_level_1" in src: slots.append(1)
            elif "gem_level_2" in src: slots.append(2)
            elif "gem_level_3" in src: slots.append(3)
            elif "decoration_level_4" in src or "gem_level_4" in src: slots.append(4)
        
        # Fallback para texto caso as imagens falhem (ex: "4-2-1")
        if not slots:
            text = cell.get_text(strip=True)
            matches = re.findall(r'[1-4]', text)
            if matches:
                slots = [int(m) for m in matches]
                
        return sorted(slots, reverse=True)

    def parse_skills(self, cell: BeautifulSoup) -> list[dict]:
        """Extrai lista de habilidades e níveis de uma célula."""
        skills = []
        links = cell.find_all("a", class_="wiki_link")
        
        if not links:
            text = cell.get_text(" ", strip=True)
            matches = re.finditer(r'([A-Za-z\s\-\']+)\s*([1-5]x|[1-5])', text)
            for m in matches:
                name = m.group(1).strip()
                if not name: continue
                level_match = re.search(r'\d', m.group(2))
                level = int(level_match.group()) if level_match else 1
                skills.append({"name": name, "level": level})
            return skills

        for link in links:
            name = link.get_text(strip=True)
            if not name or name.lower() in ["monster hunter world", "iceborne", ""]: continue
            
            level = 1
            sibling = link.next_sibling
            if sibling and isinstance(sibling, str):
                match = re.search(r'(\d+)', sibling)
                if match:
                    level = int(match.group(1))
            
            skills.append({"name": name, "level": level})
        return skills

    def parse_defense(self, text: str) -> tuple[int, int]:
        """Separa defesa base e máxima."""
        nums = re.findall(r'(\d+)', text)
        if len(nums) >= 2:
            return int(nums[0]), int(nums[1])
        if len(nums) == 1:
            return int(nums[0]), int(nums[0])
        return 0, 0

    async def scrape_armor_pieces(self, url: str, piece_type: str, rank: str):
        """Scrapeia uma página de peças de armadura."""
        html = await self.fetch(url)
        if not html: return []
        
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="wiki_table")
        if not table: return []
            
        pieces = []
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5: continue
            
            name_cell = cols[0]
            link = name_cell.find("a", class_="wiki_link")
            name = link.get_text(strip=True) if link else name_cell.get_text(strip=True)
            if not name: continue

            base_def, max_def = self.parse_defense(cols[3].get_text(strip=True))

            piece = {
                "name": name,
                "type": piece_type,
                "rank": rank,
                "rarity": cols[1].get_text(strip=True),
                "skills": self.parse_skills(cols[2]),
                "defense_base": base_def,
                "defense_max": max_def,
                "slots": self.parse_slots(cols[4]),
                "resistances": {
                    "fire": cols[5].get_text(strip=True),
                    "water": cols[6].get_text(strip=True),
                    "thunder": cols[7].get_text(strip=True),
                    "ice": cols[8].get_text(strip=True),
                    "dragon": cols[9].get_text(strip=True),
                }
            }
            pieces.append(piece)
        return pieces

    async def scrape_weapon_pieces(self, url: str, weapon_type: str, rank: str):
        """Scrapeia uma página de armas (usando Comparison Table se disponível)."""
        html = await self.fetch(url)
        if not html: return []
        
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="wiki_table")
        if not table: return []
        
        weapons = []
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5: continue
            
            # Col 0: Name + Slots (Images)
            name_cell = cols[0]
            link = name_cell.find("a", class_="wiki_link")
            name = link.get_text(strip=True) if link else name_cell.get_text(strip=True)
            if not name or name.lower() == "name": continue

            # Extração de Slots da mesma célula do nome
            slots = self.parse_slots(name_cell)

            # Raridade
            rarity_text = cols[4].get_text(strip=True)
            try:
                match_r = re.search(r'\d+', rarity_text)
                rarity = int(match_r.group()) if match_r else 0
            except:
                rarity = 0

            weapon = {
                "name": name,
                "type": weapon_type,
                "rank": rank,
                "rarity": rarity,
                "attack": cols[1].get_text(strip=True),
                "affinity": cols[2].get_text(strip=True),
                "element": cols[3].get_text(strip=True),
                "slots": slots
            }
            weapons.append(weapon)
        return weapons

async def main():
    scraper = WikiScraper()
    try:
        # Categorias de Armadura
        armor_categories = [
            ("Master+Rank+Head+Armor", "Head", "MR"),
            ("Master+Rank+Chest+Armor", "Chest", "MR"),
            ("Master+Rank+Arms+Armor", "Arms", "MR"),
            ("Master+Rank+Waist+Armor", "Waist", "MR"),
            ("Master+Rank+Leg+Armor", "Legs", "MR"),
            ("Head+Armor", "Head", "HR/LR"),
        ]
        
        all_armor = []
        for path, p_type, rank in armor_categories:
            url = f"https://monsterhunterworld.wiki.fextralife.com/{path}"
            all_armor.extend(await scraper.scrape_armor_pieces(url, p_type, rank))
        
        # Categorias de Armas (Plurais para Iceborne)
        weapon_categories = [
            ("Iceborne+Great+Swords", "Great Sword", "MR"),
            ("Iceborne+Long+Swords", "Long Sword", "MR"),
            ("Iceborne+Dual+Blades", "Dual Blades", "MR"),
            ("Iceborne+Hammers", "Hammer", "MR"),
            ("Iceborne+Hunting+Horns", "Hunting Horn", "MR"),
            ("Iceborne+Lances", "Lance", "MR"),
            ("Iceborne+Gunlances", "Gunlance", "MR"),
            ("Iceborne+Switch+Axes", "Switch Axe", "MR"),
            ("Iceborne+Charge+Blades", "Charge Blade", "MR"),
            ("Iceborne+Insect+Glaives", "Insect Glaive", "MR"),
            ("Iceborne+Light+Bowguns", "Light Bowgun", "MR"),
            ("Iceborne+Heavy+Bowguns", "Heavy Bowgun", "MR"),
            ("Iceborne+Bows", "Bow", "MR"),
        ]
        
        all_weapons = []
        for path, w_type, rank in weapon_categories:
            url = f"https://monsterhunterworld.wiki.fextralife.com/{path}"
            all_weapons.extend(await scraper.scrape_weapon_pieces(url, w_type, rank))
        
        # Salvar resultados
        Path("data/scraped_armor.json").write_text(json.dumps(all_armor, indent=2, ensure_ascii=False), encoding="utf-8")
        Path("data/scraped_weapons.json").write_text(json.dumps(all_weapons, indent=2, ensure_ascii=False), encoding="utf-8")
        
        print(f"🏁 Finalizado! {len(all_armor)} armaduras e {len(all_weapons)} armas salvas.")
            
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
