# Tasks: Optimize Weapon RAG and Search Accuracy

### 1. Data Logic and Utility Updates (mhw_tools.py)
- [x] 1.1 Standardize `MONSTER_TREE_MAP` keywords for Velkhana, Legiana, Barioth, and Beotodus.
- [x] 1.2 Implement `_get_monster_from_name` helper function.
- [x] 1.3 Update `search_equipment` to include the `monstro` field in JSON results.
- [x] 1.4 Update `get_weapon_details` to include the `monstro` field in its return dictionary.

### 2. Service and Middleware Updates (chat_service.py)
- [x] 2.1 Import `ELEMENT_MAP`, `WEAPON_MAP`, and `search_equipment` in `_extract_and_verify_equipment`.
- [x] 2.2 Implement proactive logic to detect element + weapon-type combinations.
- [x] 2.3 Trigger `search_equipment` when both element and type are detected.
- [x] 2.4 Update formatting of verified entries to include the associated monster name.

### 3. RAG Engine and Retrieval Improvements (mhw_rag.py & rag_loader.py)
- [x] 3.1 Expand "Gelo" query expansion logic to include Legiana, Barioth, and Beotodus.
- [x] 3.2 Update `_load_weapons` in `rag_loader.py` to associate monsters with documents at load time.
- [x] 3.3 Add `monster` metadata field and "Monstro: <Name>" text line to weapon documents.

### 4. Verification and Cleanup
- [x] 4.1 Verify that "todas as katanas de gelo" returns Barioth, Beotodus, Legiana, and Velkhana weapons.
- [x] 4.2 Validate that Velkhana weapons utilize the correct Portuguese translation keywords.
- [x] 4.3 Remove any temporary debug scripts.
