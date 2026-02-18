# Spec: Armor RAG Restructuring

## Purpose
This specification defines the requirements for structural improvements to how armor sets and pieces are represented in the RAG (Retrieval-Augmented Generation) system to ensure high-fidelity retrieval of build-critical information.

## Requirements

### Requirement: Structured Armor Set Documents
The RAG loader must generate a highly structured text representation for each armor set to improve LLM comprehension.

#### Scenario: Generate High-Resolution Text
- **GIVEN** An armor set with pieces (Head, Chest, Arms, Waist, Legs)
- **WHEN** The `rag_loader.py` processes the set
- **THEN** It must produce a document with a clear header, a set bonus section (if applicable), and a list of pieces where each piece has its own sub-header, defensive stats, elemental resistances, slots in `[X, Y, Z]` format, and a bulleted list of skills with levels.

### Requirement: Metadata Keyword Enrichment
Armor documents must have metadata or search-friendly text enrichment to capture common user terminology.

#### Scenario: Inject Rank and Variation Keywords
- **GIVEN** An armor piece of a specific rank (Low, High, Master) or variation (Alpha, Beta, Gamma)
- **WHEN** Generating the document text
- **THEN** It must explicitly include terms like "Master Rank", "RM", "Alfa Plus", "α+", "Beta Plus", "β+" to match common user search patterns.

### Requirement: Integrated Set Bonuses
Set bonuses must be clearly linked to the armor set document.

#### Scenario: List Set Bonus Requirements
- **GIVEN** an armor set with a bonus (e.g., Rathalos Power)
- **WHEN** Generating the set document
- **THEN** It must include the name of the bonus, its description, and the number of pieces required to activate each level of the bonus.
