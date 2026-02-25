# Spec: Build Equipment Grid

## Purpose
Define a interface visual de seleção de equipamento do Builder, incluindo a grid de peças, os slots de decoração interativos e a validação de compatibilidade de tiers de joias.

## Requirements

### Requirement: Equipment Grid Layout
A view do Builder deve exibir uma grid vertical de 8 slots de equipamento: Arma, Elmo, Peito, Braços, Cintura, Pernas, Amuleto (Charm) e Ferramenta Especializada (opcional/futuro).

#### Scenario: Slot Vazio
- **GIVEN** o Builder é aberto pela primeira vez.
- **THEN** todos os 8 slots devem exibir um placeholder com ícone genérico e texto "Selecionar [Tipo]".

#### Scenario: Selecionar Equipamento
- **WHEN** o usuário clica em um slot de equipamento vazio.
- **THEN** um modal/picker deve abrir listando todos os equipamentos disponíveis daquele tipo.
- **AND** a lista deve suportar filtro por texto (nome), monstro de origem e rank.

#### Scenario: Equipamento Selecionado
- **WHEN** o usuário seleciona uma peça no picker.
- **THEN** o slot deve exibir o nome da peça, seus slots de decoração (representados por ícones coloridos por tier) e as skills nativas.
- **AND** o painel de Summary Cards deve atualizar imediatamente.

### Requirement: Decoration Slot Interaction
Cada peça de equipamento exibe seus slots de decoração como ícones clicáveis abaixo do nome.

#### Scenario: Abrir Decoration Picker
- **WHEN** o usuário clica em um slot de decoração de tier 3.
- **THEN** um picker de joias deve abrir mostrando APENAS joias de tier 1, 2 e 3.
- **AND** joias de tier 4 devem estar visualmente bloqueadas (greyed out) com tooltip "Requer slot de nível 4".

#### Scenario: Inserir Joia Válida
- **GIVEN** um slot de tier 4.
- **WHEN** o usuário seleciona "Ataque+ Joia 4" (tier 4).
- **THEN** a joia é inserida, o ícone do slot muda para refletir a joia, e as skills atualizam.

#### Scenario: Remover Joia
- **WHEN** o usuário clica com botão direito (ou longo press) em um slot com joia.
- **THEN** a joia é removida e as skills atualizam.

### Requirement: Equipment Data API
O backend deve expor endpoints para fornecer dados completos de equipamento.

#### Scenario: Listar Armas por Tipo
- **WHEN** o frontend faz `GET /equipment/weapons?type=long-sword`.
- **THEN** retorna lista de todas as katanas com: nome (pt/en), ataque, afinidade, elemento, slots e raridade.

#### Scenario: Listar Armaduras por Slot
- **WHEN** o frontend faz `GET /equipment/armor?type=head&rank=master`.
- **THEN** retorna lista de todos os elmos Master Rank com: nome, defesa, resistências, slots e skills nativas.

#### Scenario: Listar Decorações
- **WHEN** o frontend faz `GET /equipment/decorations`.
- **THEN** retorna lista completa de joias com: nome, tier, skill concedida e nível.

#### Scenario: Listar Amuletos
- **WHEN** o frontend faz `GET /equipment/charms`.
- **THEN** retorna lista de amuletos com: nome, skill concedida e nível máximo.
