# Design: Calibrate Armor and Skills RAG Precision

## Context
The current MHWI chatbot provides accurate info on weapons but often struggles with the specific details of armors and skills. This is caused by information being scattered across multiple RAG documents without a clear structure or explicit links (e.g., matching a skill to all its armor sources). Users also use naming variations (α, β, gamma) that the current expansion logic doesn't always map correctly to the source XML data.

## Goals / Non-Goals
**Goals:**
- Implement a structured "High-Resolution" template for armor sets in `rag_loader.py`.
- Create a reverse mapping of skills to armor pieces to allow 100% accurate skill source discovery.
- Robustly handle Greek symbols and Master Rank abbreviations in query expansion.
- Ensure set bonuses are clearly explained within the armor set context.

**Non-Goals:**
- Modifying the underlying SQLite database (`mhw.db`).
- Changing the LLM model or embedding provider.
- Implementing a full build optimizer (this is just for information retrieval).

## Decisions

### 1. Structured Armor Template
Instead of unstructured text, each armor piece will be formatted using a pseudo-table structure in the RAG document:
```text
  > PEÇA: [NOME] ([TIPO])
    Rank: [RANK] | Raridade: [RARIDADE]
    Defesa: Base [X] | Máx [Y] | Aum. [Z]
    Slots: [[S1, S2, S3]]
    Resistências: Fogo=[V], Água=[V], ...
    Habilidades:
      - [SKILL 1]: Nível [L]
      - [SKILL 2]: Nível [L]
```
**Rationale**: LLMs perform significantly better at extracting specific values (like slots) when they are presented in a consistent, key-value style format.

### 2. Reverse Skill Mapping (Reverse Lookup)
We will add a dedicated loader `_load_skill_reverse_lookup` that aggregates data from `armor_skill.xml`, `charm_skill.xml`, and `decoration.xml`.
- **Output**: One document per skill tree.
- **Content**: "Habilidade [NOME] pode ser encontrada em: [Peça A (Rank)], [Amuleto B], etc."
**Rationale**: This eliminates the need for the LLM to "join" different documents at runtime, which is the primary source of hallucinations for "which armor has skill X?" questions.

### 3. Greek Symbol & Master Rank Normalization
Update `mhw_rag.py`'s `_expand_queries` to normalize:
- `a+`, `alpha+` -> `α+`
- `b+`, `beta+` -> `β+`
- `g+`, `gamma+` -> `γ+`
- `mr`, `m rank` -> `Master Rank`
**Rationale**: The XML data uses specific symbols and terms; normalizing user input at the query level ensures the retriever hits the correct documents.

## Risks / Trade-offs
- **Increased Index Size**: Adding reverse lookup documents and structured text will increase the number of tokens in the RAG storage. 
- **Mitigation**: We will use `similarity_top_k=30` (already in place) to ensure enough context is retrieved despite the larger document pool.
- **Index Rebuild Time**: A full rebuild of the RAG index will be necessary to apply these changes.
