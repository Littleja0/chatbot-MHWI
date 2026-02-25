# Spec: Enhanced Ice Recall

## Purpose
This specification defines how the system ensures high-quality retrieval for ice-element equipment, covering specific monsters and query expansion logic.

## Requirements

### Requirement: Document Tagging
Weapon documents in the RAG index must include the associated monster in their metadata to improve retrieval relevance.

### Requirement: Query Expansion
Queries involving "Ice" or "Gelo" must be automatically expanded to include specific top-tier Ice monsters.

#### Scenario: Ice Query Expansion
- **WHEN** user query contains "gelo"
- **THEN** internal RAG queries should include "CONJUNTO DE ARMADURA: Legiana", "CONJUNTO DE ARMADURA: Barioth", etc.
