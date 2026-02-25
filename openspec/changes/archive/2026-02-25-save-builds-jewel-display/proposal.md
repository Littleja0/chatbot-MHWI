# Change Proposal: Save Builds & Jewel Display

## Why

Atualmente, o Build Builder do chatbot MHW:I permite montar builds completas com armaduras, armas, jóias e augments — porém **não há forma de salvar** uma build que o jogador gostou. Toda vez que ele quer revisitar uma configuração, precisa remontar do zero. Isso é frustrante especialmente para quem testa várias variações.

Além disso, os **slots de jóias** mostram apenas um losango colorido genérico (baseado no tier), sem indicar **qual** jóia está equipada visualmente. No jogo real, cada jóia possui um ícone distinto e, ao passar o mouse, mostra a **descrição da skill** que ela concede. Essa informação visual e contextual está faltando, tornando difícil saber rapidamente o que cada jóia faz sem clicar nela.

## Scope

- **Frontend (`apps/frontend`)**: 
  - Novo sistema de "Builds Salvas" com persistência em `localStorage` e UI para listar/carregar/deletar builds.
  - Alteração visual dos slots de jóia no `EquipmentSlot.tsx` para exibir o ícone correto da jóia equipada (ao invés do losango genérico).
  - Tooltip/descrição da skill da jóia ao passar o mouse ou ao lado do slot, mostrando o que a skill faz (como no jogo).
- **Backend (`apps/backend`)**: Pode ser necessário incluir o campo `description` da skill da jóia nos dados retornados pelo endpoint `/equipment/decorations`.

## Capabilities

### New Capabilities

- `saved-builds`: Sistema de persistência de builds favoritas com localStorage. Permite ao jogador salvar a build atual com um nome, listar builds salvas, carregar uma build salva (restaurando todo o estado do Builder), deletar builds salvas e acessá-las de forma rápida via um painel lateral ou botões no Builder.

- `jewel-slot-visual`: Melhoria visual dos slots de jóia nos equipamentos. Quando uma jóia está equipada, o slot mostra um ícone que represente visualmente a jóia (usando a cor do tier + o nome abreviado ou ícone da skill), ao invés do losango genérico. Isso torna claro qual jóia está em cada slot sem precisar clicar.

- `jewel-skill-description`: Exibição da descrição do efeito da skill que a jóia concede, similar ao comportamento in-game. Pode ser via tooltip ao hover ou texto inline abaixo do slot. Inclui o nome da skill, nível concedido e uma descrição do que a skill faz.

### Modified Capabilities

- `build-equipment-grid`: Os slots de decoração no `EquipmentSlot` precisam ser atualizados para renderizar o novo visual das jóias (ícone + tooltip).

## Impact

- **Frontend**: 
  - Novo componente `SavedBuildsPanel` (painel de builds salvas).
  - Novos botões de "Salvar Build" e "Carregar Build" no `BuildExporter` ou no `BuilderView`.
  - Alteração no `EquipmentSlot.tsx` para renderizar ícones de jóia e tooltips com descrição.
  - Alteração no `DecorationPicker.tsx` para incluir descrições das skills.
  - Novo hook `useSavedBuilds` para gerenciar persistência em localStorage.
  - Adição de tipos `SavedBuild` no `types/builder.ts`.
- **Backend**: Inclusão do campo `description` da skill no endpoint de decorações (se disponível no DB).
- **Estado**: O `BuildContext` precisará de novas actions (`LOAD_BUILD`) para restaurar um estado salvo.
- **Banco de Dados**: Nenhuma alteração — dados de skills já devem existir no mhw.db.
