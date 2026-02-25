# Design: Weapon RAG and Search Optimization

## Context
The RAG system depends on context retrieval from indexed documents. However, broad queries (e.g., "all ice katanas") often return a limited set of documents that don't cover the entire weapon tree from all relevant monsters. Additionally, keyword ambiguities (e.g., "elusarca" vs "elussalka") led to hallucination or lack of verified data for specific high-tier weapons like those from Velkhana.

## Goals / Non-Goals
**Goals:**
- Implement a proactive SQL search layer that complements RAG.
- Ensure 100% accuracy in monster-weapon attribution.
- Broaden the recall of ice-type equipment.
- Standardize Portuguese weapon tree keywords.

**Non-Goals:**
- Changing the underlying database schema.
- Re-indexing the entire dataset (only logic updates for future indexing).

## Architecture
We use a **Hybrid Strategy**:
1. **RAG Expansion**: Improving the retrieval hints sent to the vector DB.
2. **Metadata Enrichment**: Adding monster tags to RAG documents at load time.
3. **Proactive SQL Trigger**: Detecting intents in `chat_service.py` to fetch "Absolute Truth" directly from SQL.

## Technical Decisions
### 1. Keyword-based Attribution
Instead of complex NLP, we use a curated `MONSTER_TREE_MAP` of known weapon tree keywords (e.g., "ladra", "glacial" -> Legiana) to map weapon names to monsters. This is fast and deterministic.

### 2. Proactive Search in Middleware
The `_extract_and_verify_equipment` function in `chat_service.py` will now double-duty as a "Proactive Searcher". If it detects a match in `ELEMENT_MAP` AND `WEAPON_MAP`, it triggers a broad `search_equipment` call.

### 3. RAG Loader Metadata
Weapon documents will now store `monster: <Name>` in their metadata. This allows future filtering in RAG queries.

## Risks / Trade-offs
- **Performance**: Proactive SQL searches add a small delay to the response generation.
- **Maintenance**: The `MONSTER_TREE_MAP` must be manually updated if new trees or variations are discovered.
