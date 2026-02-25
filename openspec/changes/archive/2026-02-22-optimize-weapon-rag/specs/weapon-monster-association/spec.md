# Spec: Weapon-Monster Association

## User Requirements
The system must be able to identify which monster a specific weapon belongs to based on its name (tree keyword). This is essential for providing contextually accurate information and preventing hallucinations where weapons are misattributed.

## ADDED Requirements

### Requirement: Keyword Mapping Accuracy
The system must maintain a mapping of "Tree Keywords" for all major monsters, particularly those in the Master Rank expansion (Iceborne).

### Requirement: Bilingual Detection
The detection logic must handle both English and Portuguese weapon names.

## Acceptance Criteria

### Scenario: Identify Velkhana Weapon
- **WHEN** searching for "Elussalka Reverente" or "Reverent Elusarca"
- **THEN** return "Velkhana" as the associated monster.

### Scenario: Identify Legiana Weapon
- **WHEN** searching for "Ladra Glacial" or "Hoarcry Stealer"
- **THEN** return "Legiana" as the associated monster.
