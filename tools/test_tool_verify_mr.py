import sys
import os
sys.path.append(os.path.join(os.getcwd(), "apps/backend/src"))

from core.mhw.mhw_tools import search_equipment
import json

def test_mr_search():
    print("--- Searching 'Velkhana' weapons (MR) ---")
    res = search_equipment(category="weapon", query_name="Velkhana", rank="MR")
    try:
        data = json.loads(res)
        print(f"Found {len(data)} items.")
        if data:
            print(json.dumps(data[0], indent=2))
    except:
        print(res)

    print("\n--- Searching 'Nargacuga' weapons (MR) ---")
    res = search_equipment(category="weapon", query_name="Nargacuga", rank="MR")
    try:
        data = json.loads(res)
        print(f"Found {len(data)} items.")
        if data:
            # Check attack values
            attacks = [d['attack'] for d in data]
            print(f"Attacks: {attacks[:5]}")
    except:
        print(res)

if __name__ == "__main__":
    test_mr_search()
