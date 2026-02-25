# Spec: Proactive Equipment Search

## User Requirements
When a user asks for a category of items (e.g., "all fire longswords"), the system should not rely solely on RAG, but should trigger a direct database query to provide a comprehensive list of verified items.

## ADDED Requirements

### Requirement: Intent Detection
The system must detect the combinations of `Element` (from `ELEMENT_MAP`) and `Weapon Type` (from `WEAPON_MAP`) in the user query.

### Requirement: Absolute Truth Verification
Every entry found via proactive search must be verified against the SQL database to ensure stats (Attack, Affinity, Element, Slots) are 100% accurate.

## Acceptance Criteria

### Scenario: Global Ice Weapon Search
- **WHEN** query contains "gelo" and "katanas" (or variants)
- **THEN** call `search_equipment(element='Ice', piece_type='long-sword')` and include all 15 top results in the "DADOS TÉCNICOS VERIFICADOS" block.
