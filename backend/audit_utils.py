
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
import re
import unicodedata

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[-\s]+', '-', value)

def fetch_fextralife_data(armor_name):
    """
    Fetches armor data from Fextralife Wiki.
    Returns: {'defense': int, 'slots': [int, int, int], 'skills': {name: level}}
    """
    # Fextralife URL Normalization
    # User Request: "a+" == "Alpha +", "b+" == "Beta +"
    # Fextralife typically uses "Name+Alpha+Plus" or "Name+Beta+Plus" or just "Name+Alpha+"
    
    # Pre-process name to normalize "a+" and "Alpha +" to a standard internal key if needed,
    # but for URL generation we need to match their specific format.
    # Common Fextralife format: "Monster+Name+Alpha+Armor+Set" or "Name+Alpha+Plus+Head" ? 
    # Actually usually: "Viper+Kadachi+Helm+Alpha+"
    
    clean_name = armor_name.strip()
    
    # Handle "Alpha +" / "a+" variations
    # Regex to catch " a+" or " alpha +" at end or followed by space
    clean_name = re.sub(r'(?i)\s+a\+', ' Alpha+', clean_name)
    clean_name = re.sub(r'(?i)\s+alpha\s+\+', ' Alpha+', clean_name)
    clean_name = re.sub(r'(?i)\s+b\+', ' Beta+', clean_name)
    clean_name = re.sub(r'(?i)\s+beta\s+\+', ' Beta+', clean_name)
    
    # Replace spaces with plus
    url_name = clean_name.replace(" ", "+")
    
    base_url = "https://monsterhunterworld.wiki.fextralife.com"
    url = f"{base_url}/{url_name}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        
        # If 404, try adding "Plus" if "Alpha+" is at end or similar variations
        # Fextralife sometimes uses "Alpha+Plus" which sounds redundant but happens in URLs?
        # Or sometimes "Alpha+Armor+Set"
        if resp.status_code != 200:
             # Variation 1: Replace "Alpha+" with "Alpha+Plus"
             if "Alpha+" in url_name:
                 var_url = f"{base_url}/{url_name.replace('Alpha+', 'Alpha+Plus')}"
                 resp = requests.get(var_url, headers=headers, timeout=5)
             
             # Variation 2: Try "Beta+" -> "Beta+Plus"
             if resp.status_code != 200 and "Beta+" in url_name:
                 var_url = f"{base_url}/{url_name.replace('Beta+', 'Beta+Plus')}"
                 resp = requests.get(var_url, headers=headers, timeout=5)

             # Variation 3: Append "+Armor+Set" (Often for full sets, but maybe individual pages redirect?)
             # Usually individual pieces are verified on the SET page if piece page doesn't exist?
             # For now, let's stick to piece pages.
             
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for "Defense" or "Slots" int the table
            # Simplified: Look for first table, check headers
            # Assume Slots logic based on images
            slots = []
            # Find the table with "Slots" or "Decoration" in header
            for table in soup.find_all('table'):
                if "Decoration" in table.text or "Slots" in table.text:
                    # Iterate rows to find Slots cell
                    # This is heuristic. Look for images like 'gem_level_X.png'
                    imgs = table.find_all('img')
                    for img in imgs:
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        if 'gem_level_1' in src or 'gem_level_1' in alt: slots.append(1)
                        elif 'gem_level_2' in src or 'gem_level_2' in alt: slots.append(2)
                        elif 'gem_level_3' in src or 'gem_level_3' in alt: slots.append(3)
                        elif 'gem_level_4' in src or 'gem_level_4' in alt: slots.append(4)
                    
                    slots.sort(reverse=True)
                    # Pad with 0 to length 3
                    while len(slots) < 3: slots.append(0)
                    
                    res = []
                    for i in range(3):
                        res.append(slots[i])
                    return {'slots': res}
        return None
    except Exception as e:
        print(f"Error fetching Fextralife for {armor_name}: {e}")
        return None

def fetch_kiranico_data(armor_name, armor_type):
    """
    Fetches armor data from Kiranico.
    Returns compatible dict.
    """
    # URL Guessing
    # armor_type: head, chest, arms, waist, legs
    # e.g. Beotodus Helm Beta+ -> beotodus-helm-beta-plus
    name_slug = armor_name.lower().replace(" ", "-").replace("β+", "beta-plus").replace("α+", "alpha-plus").replace("+", "-plus")
    type_slug = armor_type # already short usually
    
    url = f"https://mhworld.kiranico.com/en/armors/{type_slug}/{name_slug}"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code != 200:
            return None
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Kiranico slots
        # Look for images with 'slot_' in src
        slots = []
        # Usually in a table
        tables = soup.find_all('table')
        if tables:
            # First table usually has stats
            main_table = tables[0]
            imgs = main_table.find_all('img')
            for img in imgs:
                src = img.get('src', '')
                if 'slot_1' in src: slots.append(1)
                elif 'slot_2' in src: slots.append(2)
                elif 'slot_3' in src: slots.append(3)
                elif 'slot_4' in src: slots.append(4)
            
            slots.sort(reverse=True)
            while len(slots) < 3: slots.append(0)
            
            res = []
            for i in range(3):
                res.append(slots[i])
            return {'slots': res}
            
        return None
    except Exception as e:
        print(f"Error fetching Kiranico for {armor_name}: {e}")
        return None
