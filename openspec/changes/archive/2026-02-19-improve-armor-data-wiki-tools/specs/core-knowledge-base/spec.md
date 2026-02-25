# Spec: core-knowledge-base (Dados Wiki)

Definição dos requisitos para a extração e armazenamento de dados da Wiki Fextralife.

## Requisitos de Dados

### Requirement: Esquema do Banco de Dados (SQL)
As tabelas no `mhw.db` devem seguir a estrutura:
- **Tabela `wiki_armor`**:
  - `id`: TEXT (PK)
  - `name_en`: TEXT
  - `name_pt`: TEXT (se disponível)
  - `rank`: TEXT (LR, HR, MR)
  - `piece_type`: TEXT (Head, Chest, Arms, Waist, Legs)
  - `slots`: TEXT (ex: "4,2,0" ou "1,1,1")
  - `defense_base`: INT
  - `defense_max`: INT
  - `rarity`: INT
- **Tabela `wiki_armor_skills`**:
  - `id`: INTEGER (PK AUTOINCREMENT)
  - `armor_id`: TEXT (FK)
  - `skill_name`: TEXT
  - `level`: INT

### Requirement: Scraper Robustez
- O scraper deve lidar com falhas de conexão usando retentativas (retry logic).
- Deve salvar o HTML bruto localmente como cache para evitar sobrecarga no servidor da Wiki.
- Deve extrair o número correto de slots (0-4) e o nível de cada slot.

## Critérios de Aceitação
- **GIVEN** uma execução completa do scraper para Master Rank.
- **WHEN** consultamos o banco por "Teostra Head Beta +".
- **THEN** os slots retornados devem ser exatamente `[4, 1, 0]` e a skill "Critical Eye" nível 2.
