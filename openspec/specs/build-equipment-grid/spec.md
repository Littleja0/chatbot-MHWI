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
- **THEN** retorna lista completa de joias con: nome, tier, skill concedida e nível.

#### Scenario: Listar Amuletos
- **WHEN** o frontend faz `GET /equipment/charms`.
- **THEN** retorna lista de amuletos com: nome, skill concedida e nível máximo.

### Requirement: Renderização de Slots de Jóia Atualizada
O componente `EquipmentSlot` usa um visual aprimorado para jóias preenchidas.

#### Scenario: Jóia Equipada com Visual de Iniciais
- **GIVEN** o componente `EquipmentSlot` renderiza slots de decoração.
- **WHEN** um slot tem uma jóia equipada.
- **THEN** renderiza o visual com iniciais da skill (ex: "At" para Reforço de Ataque) com fundo colorido no tier.
- **AND** adiciona tooltip de hover com nome da jóia, skills e descrições.
- **AND** mantém o comportamento de clique direito para remover.

### Requirement: Slots com Tooltip Não Interferem no Layout
Os tooltips de jóias não afetam o layout do EquipmentSlot.

#### Scenario: Tooltip Aparece sem Empurrar
- **GIVEN** o jogador hover sobre um slot de jóia em um equipamento.
- **WHEN** o tooltip aparece.
- **THEN** o tooltip usa `position: absolute` e não empurra outros elementos.
- **AND** o tooltip é renderizado dentro do `deco-slot` button com overflow visible.

### Requirement: Dados da Jóia para Tooltip
O `EquipmentSlot` recebe os dados completos da jóia (incluindo descrição) para renderizar o tooltip.

#### Scenario: Tooltip com Descrição
- **GIVEN** o `BuilderView` passa a prop `decorations` para o `EquipmentSlot`.
- **WHEN** as jóias incluem o campo `description` nas skills.
- **THEN** o `EquipmentSlot` renderiza o tooltip com nome, nível e descrição.
- **AND** se `description` não estiver presente, o tooltip mostra apenas nome e nível.
