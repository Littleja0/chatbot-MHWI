# Spec: Enhanced Query Expansion

## Purpose
This specification defines requirements for robust query expansion and normalization to handle variations in user terminology for armors and skills.

## Requirements

### Requirement: Armor Variation Normalization
The `mhw_rag.py` logic must expand queries to include all possible variations of armor naming conventions.

#### Scenario: Expand Greek Symbols and Abbreviations
- **GIVEN** a prompt like "rathalos b+"
- **WHEN** the `_expand_queries` function is called
- **THEN** it must generate additional queries including "Rathalos β+", "Rathalos Beta Plus", and "CONJUNTO DE ARMADURA: Rathalos β+".

### Requirement: Skill-Specific Query Targeting
Queries about skills should trigger searches specifically targeted at the reverse-lookup documents.

#### Scenario: Detect Skill Discovery Intent
- **GIVEN** a prompt like "quais armaduras tem ponto em ataque"
- **WHEN** the expansion logic detects skill keywords
- **THEN** it must generate queries specifically prefixed with "SKILL:" or "REVERSE LOOKUP:" to prioritize the new skill mapping documents.
