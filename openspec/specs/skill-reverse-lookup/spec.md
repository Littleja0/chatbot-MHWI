# Spec: Skill Reverse Lookup

## Purpose
This specification defines the requirements for a reverse mapping system that allows users to discover equipment sources for specific skills efficiently.

## Requirements

### Requirement: Skill-to-Armor Mapping
The RAG loader must generate documents that list all armor pieces and charms that provide a specific skill.

#### Scenario: Generate Reverse Lookup Document
- **GIVEN** a skill (e.g., Attack Boost)
- **WHEN** The `rag_loader.py` processes all game data
- **THEN** It must create a document for that skill that lists every armor piece, charm, and decoration that provides it, including the level provided by each source.

### Requirement: Structured Level Breakdown
The reverse lookup must be organized in a way that the LLM can easily identify the "best" sources for a skill.

#### Scenario: Categorize Sources by Rank
- **GIVEN** a list of sources for a skill
- **WHEN** Generating the reverse lookup text
- **THEN** It should group sources by Rank (Master Rank, High Rank, Low Rank) and Piece Type (Head, Chest, etc.) to help the user find the most relevant pieces for their current progress.
