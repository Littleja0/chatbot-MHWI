# Spec: Weapon-Monster Association

## Purpose
This specification defines how weapons are associated with their originating monsters. This association is crucial for providing accurate context and preventing hallucinations in equipment recommendations.

## Requirements

### Requirement: Keyword Mapping Accuracy
The system must maintain a mapping of "Tree Keywords" for all major monsters, particularly those in the Master Rank expansion (Iceborne).

#### Scenario: Identify Velkhana Weapon
- **WHEN** searching for "Elussalka Reverente" or "Reverent Elusarca"
- **THEN** return "Velkhana" as the associated monster.

### Requirement: Bilingual Detection
The detection logic must handle both English and Portuguese weapon names.

#### Scenario: Identify Legiana Weapon
- **WHEN** searching for "Ladra Glacial" or "Hoarcry Stealer"
- **THEN** return "Legiana" as the associated monster.
