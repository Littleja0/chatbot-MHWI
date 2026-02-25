# Tasks: Save Builds & Jewel Display

## 1. Backend — Descrição da Skill nas Decorações

- [x] 1.1 Alterar o endpoint `list_decorations` em `apps/backend/src/api/routers/equipment.py` para buscar o campo `description` da tabela `skilltree_text` junto com o nome da skill. Substituir a chamada `_get_text` por uma query que retorne `name` e `description`. Fazer fallback para inglês se PT não existir.
- [x] 1.2 Incluir o campo `"description"` em cada objeto do array `skills` na resposta JSON das decorações. Valor padrão: string vazia se nulo.
- [x] 1.3 Testar o endpoint com `curl` ou navegador para verificar que as descrições são retornadas corretamente em português.

## 2. Tipos e Utilitários Frontend

- [x] 2.1 Adicionar campo `description?: string` na interface `SkillRef` em `apps/frontend/src/types/builder.ts`.
- [x] 2.2 Adicionar interface `SavedBuild` em `apps/frontend/src/types/builder.ts` com campos: `id`, `name`, `createdAt`, `updatedAt`, `buildState`.
- [x] 2.3 Criar arquivo `apps/frontend/src/utils/buildHelpers.ts` com a função `abbreviateSkill(skillName: string): string` que gera iniciais de skills (ignorando preposições "de", "a", "do", "da", "em").

## 3. BuildContext — Action LOAD_BUILD

- [x] 3.1 Adicionar `LOAD_BUILD` ao tipo `BuildAction` em `apps/frontend/src/contexts/BuildContext.tsx` com payload `BuildState`.
- [x] 3.2 Implementar o case `LOAD_BUILD` no `buildReducer` que substitui o estado inteiro pelo payload.

## 4. Hook useSavedBuilds

- [x] 4.1 Criar `apps/frontend/src/hooks/useSavedBuilds.ts` com o hook que gerencia builds no `localStorage` (chave `mhwi-saved-builds`).
- [x] 4.2 Implementar `saveBuild(name, state)` — gera UUID, cria `SavedBuild`, persiste no localStorage.
- [x] 4.3 Implementar `loadBuild(id)` — retorna o `BuildState` da build salva.
- [x] 4.4 Implementar `deleteBuild(id)` — remove do array e persiste.
- [x] 4.5 Implementar `renameBuild(id, newName)` — atualiza nome e `updatedAt`.
- [x] 4.6 Implementar propriedade `isAtLimit` — retorna `true` quando `savedBuilds.length >= 50`.

## 5. Componente SavedBuildsPanel

- [x] 5.1 Criar `apps/frontend/src/components/builder/SavedBuildsPanel.tsx` com painel colapsável de builds salvas.
- [x] 5.2 Implementar botão "💾 Salvar Build" que abre input para nome. Desabilitado se nenhuma arma selecionada ou se `isAtLimit`.
- [x] 5.3 Implementar lista de builds salvas mostrando: nome, arma, EFR e data relativa.
- [x] 5.4 Implementar botão "Carregar" com confirmação se build atual tem equipamentos. Dispatch `LOAD_BUILD`.
- [x] 5.5 Implementar botão "Excluir" com confirmação antes de remover.
- [x] 5.6 Implementar edição inline do nome da build (clique no nome → input editável → Enter/blur para confirmar).
- [x] 5.7 Adicionar o `SavedBuildsPanel` no `BuilderView.tsx` logo abaixo do `BuildExporter`.

## 6. Visual dos Slots de Jóia

- [x] 6.1 Alterar o componente `EquipmentSlot.tsx` — quando a jóia está equipada, renderizar `deco-slot__jewel-icon` com as iniciais da skill (usando `abbreviateSkill`) ao invés do `deco-slot__diamond`.
- [x] 6.2 Manter o `deco-slot__diamond` para slots vazios (comportamento atual inalterado).
- [x] 6.3 Estilizar `.deco-slot__jewel-icon` e `.deco-slot__jewel-abbr` no `Builder.css` — fundo com cor do tier (semi-transparente), borda sólida, texto centralizado em fonte pequena bold.

## 7. Tooltip de Descrição da Skill

- [x] 7.1 Adicionar markup de tooltip dentro do slot de jóia preenchido no `EquipmentSlot.tsx` — `<div className="deco-tooltip">` com nome da jóia, skill(s) e descrição(ões).
- [x] 7.2 Estilizar o tooltip no `Builder.css`:
  - Fundo escuro com `backdrop-filter: blur` (glassmorphism)
  - Borda na cor do tier
  - `position: absolute`, `z-index: 200`
  - Animação `fadeIn` suave
  - `pointer-events: none` para não interferir no hover
- [x] 7.3 Implementar visibilidade via CSS: `.deco-slot:hover .deco-tooltip { opacity: 1; visibility: visible }`.
- [x] 7.4 Garantir que o tooltip do `deco-slot` tenha `overflow: visible` para não ser cortado pelo container pai.

## 8. Descrição no DecorationPicker

- [x] 8.1 Alterar `DecorationPicker.tsx` para exibir a descrição da skill principal abaixo das skill tags em cada item da lista de jóias compatíveis.
- [x] 8.2 Estilizar a descrição com texto truncado (`text-overflow: ellipsis`, `max-width`, font menor e cor mais tênue).

## 9. CSS e Polish

- [x] 9.1 Adicionar estilos do `SavedBuildsPanel` no `Builder.css` (painel colapsável, lista de builds, botões de ação, input de nome).
- [x] 9.2 Garantir responsividade — o painel de builds salvas deve funcionar em telas menores (stack vertical se necessário).
- [x] 9.3 Testar visualmente: slots de jóia com diferentes tiers, tooltips posicionados corretamente, painel de builds com 0, 1 e vários itens.
- [x] 9.4 Build final: rodar `npm run build` no frontend e verificar que não há erros de compilação.
