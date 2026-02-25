# Spec: Enhanced Ice Recall

## User Requirements
The system must ensure that information about Ice element monsters (Legiana, Velkhana, Barioth, Beotodus) is retrieved effectively during RAG sessions involving ice equipment.

## ADDED Requirements

### Requirement: Document Tagging
Weapon documents in the RAG index must include the associated monster in their metadata to improve retrieval relevance.

### Requirement: Query Expansion
Queries involving "Ice" or "Gelo" must be automatically expanded to include specific top-tier Ice monsters.

## Acceptance Criteria

### Scenario: Ice Query Expansion
- **WHEN** user query contains "gelo"
- **THEN** internal RAG queries should include "CONJUNTO DE ARMADURA: Legiana", "CONJUNTO DE ARMADURA: Barioth", etc.
