# Proposal: Calibrate Armor and Skills RAG

## Why
Currently, the chatbot's RAG (Retrieval-Augmented Generation) system for Monster Hunter World: Iceborne (MHWI) is less precise when handling armor sets and skills compared to weapons. This is due to fragmented context, inconsistent naming (abbreviations vs. full names), and lack of explicit mapping between skills and the armor pieces that provide them. This change aims to restructure the RAG document generation to provide high-resolution, structured data that minimizes hallucinations and improves recall.

## What Changes
- Refactor `rag_loader.py` to generate structured "High Resolution" text for armor sets, including explicit tables for pieces, slots, and skills.
- Enhance metadata enrichment for armor documents to include common user keywords (Alpha, Beta, Master Rank, etc.).
- Implement a reverse lookup mechanism for skills to explicitly list which armor pieces provide each skill level.
- Improve query expansion in `mhw_rag.py` to better handle armor-specific terminology and symbols (α, β, γ).

## Capabilities
- **armor-rag-restructuring**: New structured format for armor set documents in the RAG pipeline.
- **skill-reverse-lookup**: Reverse mapping of skills to armor pieces within the RAG context.
- **enhanced-query-expansion**: Improved detection and expansion of armor/skill related queries.

## Impact
- `apps/backend/src/core/mhw/rag_loader.py`: Primary logic for parsing XMLs into RAG documents.
- `apps/backend/src/core/mhw/mhw_rag.py`: Query expansion and retrieval logic.
- RAG Storage: Rebuilding the vector index will be required.
