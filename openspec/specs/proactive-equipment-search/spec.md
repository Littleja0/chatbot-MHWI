# Spec: Proactive Equipment Search

## Purpose
This specification defines the proactive search mechanism that complements RAG by performing direct SQL queries for broad equipment categories (e.g., specific weapon types combined with specific elements).

## Requirements

### Requirement: Intent Detection
The system must detect the combinations of `Element` (from `ELEMENT_MAP`) and `Weapon Type` (from `WEAPON_MAP`) in the user query.

### Requirement: Absolute Truth Verification
Every entry found via proactive search must be verified against the SQL database to ensure stats (Attack, Affinity, Element, Slots) are 100% accurate.

#### Scenario: Global Ice Weapon Search
- **WHEN** query contains "gelo" and "katanas" (or variants)
- **THEN** call `search_equipment(element='Ice', piece_type='long-sword')` and include all 15 top results in the "DADOS TÉCNICOS VERIFICADOS" block.
