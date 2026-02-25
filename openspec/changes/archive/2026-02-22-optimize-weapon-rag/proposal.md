# Proposal: Optimize Weapon RAG and Search Accuracy

## Motivation
The current RAG system often fails to retrieve complete and accurate weapon information, particularly for specific elemental trees (like Ice) and monsters (Velkhana, Legiana). Users reported inaccuracies (e.g., Legiana weapons being attributed to Velkhana) and missing results for broad queries like "todas as katanas de gelo" (all ice katanas), which excluded weapons from Barioth and Beotodus.

## What Changes
We will implement a multi-layered approach to ensure "Absolute Truth" from SQL data is used alongside RAG:
- **Data Enrichment**: Associate weapons with their parent monsters in both the RAG indexing process and SQL search results.
- **Proactive Search**: Detect element and weapon type combinations in user queries to perform exhaustive SQL searches, bypassing RAG limitations for broad categories.
- **Query Expansion**: Enlarge the "Ice" query expansion set to include relevant monsters (Barioth, Beotodus, Legiana).
- **Terminology Fixes**: Correct internal keyword mappings for Velkhana and Legiana to match official Portuguese translations.

## Capabilities
- **weapon-monster-association**: Capability to robustly link weapon IDs and names to their originating monster using keyword-based tree mapping.
- **proactive-equipment-search**: Capability to trigger direct database searches when users query for broad equipment categories (e.g., "gelo" + "katanas").
- **enhanced-ice-recall**: Capability to broaden the search context for ice-related queries to include all relevant top-tier ice monsters.

## Impact
- `apps/backend/src/core/mhw/mhw_tools.py`: Updates to search logic and monster mapping.
- `apps/backend/src/services/chat_service.py`: updates to the anti-hallucination middleware for proactive searching.
- `apps/backend/src/core/mhw/mhw_rag.py`: Updates to query expansion logic.
- `apps/backend/src/core/mhw/rag_loader.py`: Updates to document metadata for weapon associations.
