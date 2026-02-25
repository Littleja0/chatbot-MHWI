# Purpose

Esta especificação define os requisitos para a melhoria da granularidade e precisão na recuperação de dados de armaduras (RAG) no chatbot de Monster Hunter World: Iceborne. O objetivo é permitir que o sistema distinga peças individuais de armadura, interprete corretamente os slots de decoração e forneça contexto rico (como bônus de set) mesmo em consultas granulares.

# Requirements

## Requirements

### Requirement: Indexação Individual de Peças de Armadura
O sistema SHALL criar um documento de RAG independente para cada peça de armadura individual (Cabeça, Peito, Braços, Cintura e Pernas), além do documento de conjunto (set).

#### Scenario: Recuperação de peça específica
- **WHEN** o usuário perguntar sobre o "Elmo Nargacuga Beta"
- **THEN** o sistema SHALL recuperar o documento específico dessa peça, contendo apenas seus slots e habilidades.

### Requirement: Formatação Semântica de Slots de Decoração
O sistema SHALL converter a representação numérica de slots de decoração em uma descrição textual por extenso para facilitar a interpretação pelo Modelo de Linguagem (LLM).

#### Scenario: Formatação de slots master rank
- **WHEN** uma peça de armadura possuir slots de níveis [4, 2, 0]
- **THEN** o texto gerado no documento de RAG SHALL ser "1 slot de Nível 4, 1 slot de Nível 2".

### Requirement: Expansão de Query para Granularidade de Armaduras
O sistema SHALL expandir as queries do usuário para incluir termos específicos de variações de armaduras (Alfa, Beta, Gamma) e variações regionais de tradução (α, β, γ).

#### Scenario: Busca por variação grega
- **WHEN** o usuário digitar "set narga b+"
- **THEN** o sistema SHALL incluir na busca termos como "Nargacuga β+", "Nargacuga Beta" e "CONJUNTO DE ARMADURA: Nargacuga β+".

### Requirement: Enriquecimento de Contexto com Habilidade de Set
Cada documento de peça individual SHALL conter uma menção clara ao bônus de conjunto (Set Bonus) ao qual pertence, permitindo que o LLM responda sobre bônus mesmo consultando apenas uma peça.

#### Scenario: Consulta de bônus via peça única
- **WHEN** o LLM ler o documento da "Cota de Rathalos"
- **THEN** ele SHALL encontrar a informação "Bônus de Conjunto: Maestria de Rathalos (Crítico Elemental)".
