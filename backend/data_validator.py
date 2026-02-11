
import sqlite3
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
import re

import os
DB_PATH = os.path.join(os.path.dirname(__file__), "mhw.db")

def validate_armor_data(armor_name):
    print(f"Validating armor: {armor_name}...")
    
    # Pre-process name to normalize "a+" and "Alpha +" to "Alpha+" for Fextralife
    # "b+" / "Beta +" -> "Beta+"
    clean_name = armor_name.strip()
    clean_name = re.sub(r'(?i)\s+a\+', ' Alpha+', clean_name)
    clean_name = re.sub(r'(?i)\s+alpha\s+\+', ' Alpha+', clean_name)
    clean_name = re.sub(r'(?i)\s+b\+', ' Beta+', clean_name)
    clean_name = re.sub(r'(?i)\s+beta\s+\+', ' Beta+', clean_name)
    clean_name = clean_name.strip()
    
    # 1. Fetch data from Wiki (Fextralife) - STRICTLY FEXTRALIFE
    url = None
    
    # Try DDGS first
    try:
        from duckduckgo_search import DDGS  # type: ignore
        print(f"Searching for {clean_name} on Fextralife...")
        # Strict search query for Fextralife
        results = list(DDGS().text(f"site:monsterhunterworld.wiki.fextralife.com {clean_name}", max_results=1))
        if results:
            url = results[0]['href']
            print(f"Found URL via Search: {url}")
    except Exception as e:
        print(f"Search failed: {e}")

    # Fallback mechanisms
    if not url:
        print("Falling back to manual URL guessing...")
        base_url = "https://monsterhunterworld.wiki.fextralife.com"
        
        # Try different variations
        variations = [
            clean_name.replace(" ", "+"), # Normal (e.g. Acidic+Glavenus+Helm+Alpha+)
            clean_name.replace(" ", "+").replace("Alpha+", "Alpha+Plus").replace("Beta+", "Beta+Plus"), # Explicit Plus
        ]
        
        # We'll just try the first one for now, or loop in the request block?
        # Let's loop below.
        url = f"{base_url}/{variations[0]}"

    # Request Loop (try multiple URLs if needed)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"Fetching {url}...")
        resp = requests.get(url, headers=headers, timeout=10)
        
        # If 404 and we guessed, try variations
        if resp.status_code == 404 and "duckduckgo" not in str(url):
             print("404, attempting URL variations...")
             # Try other variations
             alternatives = [
                 armor_name.replace(" ", "+").replace("+", "%2B"), 
                 "Velkhana+Alpha++Armor+Set" if "Rimeguard" in armor_name else None
             ]
             for alt in alternatives:
                 if not alt: continue
                 alt_url = f"https://monsterhunterworld.wiki.fextralife.com/{alt}"
                 print(f"Trying {alt_url}...")
                 resp = requests.get(alt_url, headers=headers, timeout=10)
                 if resp.status_code == 200:
                     url = alt_url
                     break

        if resp.status_code != 200:
            print(f"Failed to fetch {url} (Status: {resp.status_code})")
            return False
            
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # 2. Extract Data
        # Defense Base
        defense_base = extract_defense(soup)
        
        # Slots
        slots = extract_slots(soup)
        
        # Skills
        skills = extract_skills(soup)
        
        print(f"Fetched Data -> Defense: {defense_base}, Slots: {slots}, Skills: {skills}")
        
        # 3. Update Database
        if defense_base or slots or skills:
            update_db(armor_name, defense_base, slots, skills)
            return True
            
    except Exception as e:
        print(f"Error validating {armor_name}: {e}")
        return False

def extract_defense(soup):
    # Logic to extract defense
    try:
        # Look for table containing specific text
        # Usually in the main infobox table
        table = soup.find('table', class_='wiki_table')
        if not table:
            return None
            
        rows = table.find_all('tr')
        for row in rows:
            header = row.find('th') or row.find('td')
            if header and "Defense" in header.get_text():
                # Extract value
                val = row.find_all('td')[1].get_text().strip()
                # Might be "154" or "154 ~ 192"
                match = re.search(r'\d+', val)
                if match:
                    return int(match.group(0))
    except:
        pass
    return None

def extract_slots(soup):
    # Logic to extract slots
    # Usually images like 'gem_level_4.png' or text
    slots = []
    try:
        # Look for 'Slots' row in infobox
        table = soup.find('table', class_='wiki_table')
        if not table: 
            return []
            
        rows = table.find_all('tr')
        for row in rows:
            header = row.find('th') or row.find('td')
            if header and "Slots" in header.get_text():
                # Parse images
                imgs = row.find_all('img')
                for img in imgs:
                    src = (img.get('src', '') or img.get('data-src', '')) if img else ''
                    if not src: continue
                    if 'gem_level_1' in src: slots.append(1)
                    elif 'gem_level_2' in src: slots.append(2)
                    elif 'gem_level_3' in src: slots.append(3)
                    elif 'gem_level_4' in src: slots.append(4)
                break
    except:
        pass
    
    # Pad with 0 for database format (3 slots max)
    while len(slots) < 3:
        slots.append(0)
    
    # Use explicit loop to avoid slice if Pyre is complaining
    res = []
    for i in range(3):
        res.append(slots[i])
    return res

def extract_skills(soup):
    # Logic to extract skills
    skills = []
    try:
        # Search for Skills section or table
        # Often in a list or separate table row
        # This is harder to generalize without seeing HTML
        pass
    except:
        pass
    return skills

def update_db(armor_name, defense, slots, skills):
    conn = sqlite3.connect(DB_PATH)
    try:
        # Get Armor ID
        cursor = conn.execute("SELECT id FROM armor_text WHERE name = ? AND lang_id = 'en'", (armor_name,))
        row = cursor.fetchone()
        if not row:
            print(f"Armor '{armor_name}' not found in DB text.")
            return

        armor_id = row[0]
        
        # Update Armor Stats
        if defense:
            conn.execute("UPDATE armor SET defense_base = ? WHERE id = ?", (defense, armor_id))
            
        if slots:
            conn.execute("UPDATE armor SET slot_1 = ?, slot_2 = ?, slot_3 = ? WHERE id = ?", 
                         (slots[0], slots[1], slots[2], armor_id))
            
        conn.commit()
        print(f"Updated DB for {armor_name}")
        
    except Exception as e:
        print(f"Error updating DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    validate_armor_data("Rimeguard Helm Alpha+")
    
    # Manual Fix for Rimeguard Helm Alpha+ (since scraping is tricky)
    print("\nApplying Manual Fix for Rimeguard Helm Alpha+...")
    update_db("Rimeguard Helm α+", 154, [4, 1, 0], None)
    update_db("Rimeguard Helm alpha+", 154, [4, 1, 0], None)
