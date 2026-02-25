# Tasks: Interactive Build Builder

## 1. Infraestrutura & Navegação

- [x] 1.1 Adicionar estado `activeTab` no `App.tsx` e passar como props para o `Header.tsx`.
- [x] 1.2 Atualizar `Header.tsx` para aceitar `activeTab` e `onTabChange` como props e ativar a aba "Builds".
- [x] 1.3 Renderizar condicionalmente `ChatArea` ou `BuilderView` no `App.tsx` com base no `activeTab`.
- [x] 1.4 Garantir preservação de estado ao trocar entre abas (Chat e Builder não desmontam).

## 2. Build Types & Context

- [x] 2.1 Criar tipos TypeScript para o Builder em `types/builder.ts`: `BuildState`, `WeaponSlot`, `ArmorSlot`, `CharmSlot`, `DecorationSlot`, `Augment`, `CustomUpgrade`, `SafiAwakening`, `ComputedStats`, `SkillLevel`, `SetBonus`.
- [x] 2.2 Criar `BuildContext.tsx` com `useReducer` para gerenciar o `BuildState` (actions: `setWeapon`, `setArmor`, `setCharm`, `addDecoration`, `removeDecoration`, `setAugments`, `setSafiAwakenings`, `setCustomUpgrades`, `resetBuild`).
- [x] 2.3 Envolver o `App.tsx` com `<BuildProvider>` ao lado do `<ChatProvider>` existente.

## 3. Backend — Endpoints de Equipamento

- [x] 3.1 Criar arquivo `apps/backend/src/routes/equipment.py` com router FastAPI dedicado.
- [x] 3.2 Implementar `GET /equipment/weapons` — listar armas com filtros (`type`, `element`, `rank`). Usar `mhw_api.get_weapon_info` como base, expandindo para listagem completa.
- [x] 3.3 Implementar `GET /equipment/armor` — listar armaduras com filtros (`type`: head/chest/arms/waist/legs, `rank`). Retornar skills nativas e slots.
- [x] 3.4 Implementar `GET /equipment/decorations` — listar todas as joias com tier e skill concedida.
- [x] 3.5 Implementar `GET /equipment/charms` — listar amuletos com skills e níveis.
- [x] 3.6 Implementar `GET /equipment/set-bonuses` — listar set bonuses com peças necessárias e efeitos (incluindo Skill Secrets).
- [x] 3.7 Registrar o router de equipment no `main.py` do backend.
- [x] 3.8 Adicionar funções de API no frontend `apiService.ts` para consumir os novos endpoints (`getWeapons`, `getArmor`, `getDecorations`, `getCharms`, `getSetBonuses`).

## 4. Frontend — Layout do Builder

- [x] 4.1 Criar componente `BuilderView.tsx` — layout de duas colunas (Equipment Grid à esquerda, Summary Cards à direita).
- [x] 4.2 Criar componente `EquipmentSlot.tsx` — card clicável para cada peça de equipamento (Arma, Elmo, Peito, Braços, Cintura, Pernas, Amuleto). Exibir nome, ícone, slots de decoração e skills nativas.
- [x] 4.3 Criar componente `EquipmentPicker.tsx` — modal/panel com lista de equipamentos filtrável por texto, monstro e rank. Abrir ao clicar em um `EquipmentSlot` vazio ou no botão "trocar".
- [x] 4.4 Estilizar `BuilderView`, `EquipmentSlot` e `EquipmentPicker` com design premium (glassmorphism, gradientes, hover effects) consistente com o visual do app.

## 5. Frontend — Decoração (Joias)

- [x] 5.1 Criar componente `DecorationPicker.tsx` — modal que lista joias filtradas por tier do slot clicado. Joias de tier acima do slot devem aparecer bloqueadas (greyed out).
- [x] 5.2 Implementar lógica `canInsertDecoration(slotTier, decoTier)` no `BuildContext`, incluindo validação para tiles de 4 acomodarem qualquer tier.
- [x] 5.3 Renderizar ícones de slot de decoração dentro de cada `EquipmentSlot` — coloridos por tier (cinza=1, verde=2, azul=3, dourado=4). Clicar abre o `DecorationPicker`.
- [x] 5.4 Implementar remoção de joia via clique direito/long press com confirmação visual.

## 6. Frontend — Weapon Customization (Safi/Kulve/Augments)

- [x] 6.1 Criar componente `WeaponCustomizer.tsx` — painel abaixo do slot de arma com 3 seções colapsáveis: Safi Awakenings, Custom Upgrades (Kulve), Augmentations.
- [x] 6.2 Criar tabela de lookup `data/safiAwakenings.ts` — mapeamento de todas as awakened abilities com valores numéricos (Attack I-VI, Sharpness I-VI, Affinity I-VI, Slot Upgrade, Set Bonus Essences).
- [x] 6.3 Criar tabela de lookup `data/augmentations.ts` — lista de augments com custo em slots, efeitos e limites por raridade (R10: 5 slots, R11: 4, R12: 3).
- [x] 6.4 Criar tabela de lookup `data/customUpgrades.ts` — valores incrementais dos 7 níveis de Custom Upgrade (Attack, Affinity, Element, Defense).
- [x] 6.5 Implementar a lógica de "Safi Essence = +1 peça do set" no cálculo de Set Bonuses dentro do `BuildContext`.
- [x] 6.6 Implementar a lógica de "Kjarr = Critical Element embutido" — adicionar skill automática na lista de skills ativas ao selecionar arma Kjarr.
- [x] 6.7 O `WeaponCustomizer` só aparece se a arma selecionada for do tipo Safi/Kulve/Customizável.

## 7. Frontend — Stats Engine (EFR)

- [x] 7.1 Criar módulo `utils/calcEngine.ts` com funções puras para cálculo de EFR.
- [x] 7.2 Implementar `calculateTrueRaw(weapon, skills, augments, safiAwakenings, customUpgrades)` — retorna True Raw com todos os bônus.
- [x] 7.3 Implementar `calculateAffinity(weapon, skills, augments)` — retorna afinidade efetiva total.
- [x] 7.4 Implementar `calculateEFR(trueRaw, sharpness, affinity, critBoostLevel)` — fórmula final.
- [x] 7.5 Implementar `calculateElementalEFR(elementBase, sharpnessColor, skills)` — dano elemental efetivo.
- [x] 7.6 Criar tabela de lookup `data/weaponMultipliers.ts` — bloat values por tipo de arma (GS: 4.8, LS: 3.3, etc.).
- [x] 7.7 Criar tabela de lookup `data/sharpnessMultipliers.ts` — multiplicadores raw e elemental por cor.
- [x] 7.8 Criar tabela de lookup `data/skillBonuses.ts` — mapeamento de skills ofensivas e seus bônus por nível (Attack Boost 1-7, Critical Eye 1-7, Agitator 1-7, WEX 1-3, Critical Boost 1-3, etc.).
- [x] 7.9 Integrar `calcEngine` no `BuildContext` — recalcular `ComputedStats` via `useMemo` sempre que o `BuildState` mudar.

## 8. Frontend — Skills Summary & Set Bonuses

- [x] 8.1 Criar componente `SkillBar.tsx` — barra segmentada para uma skill individual. Suporte a: segmentos normais, segmentos "secret" (glow), segmentos "desperdiçados" (vermelho).
- [x] 8.2 Criar componente `SkillsSummaryPanel.tsx` — lista vertical de `SkillBar` para todas as skills ativas, ordenadas por nível decrescente.
- [x] 8.3 Criar tabela de lookup `data/skillSecrets.ts` — mapeamento de set bonuses que desbloqueiam secrets (Raging Brachy, Gold Rathian, Fatalis, etc.) com número de peças necessárias.
- [x] 8.4 Implementar lógica de Dynamic Caps no `BuildContext`: verificar peças equipadas + Safi Essences, determinar quais secrets estão ativos, ajustar `maxLevel` de cada skill.
- [x] 8.5 Criar componente `SetBonusCard.tsx` — card com nome do set bonus, progresso (ex: 2/3 peças), status (ativo/inativo) e descrição do efeito.
- [x] 8.6 Criar componente `StatsPanel.tsx` — painel de estatísticas de combate (True Raw, Display Attack, Afinidade, EFR, Elemento, Defesa). Exibir com formatação visual (números grandes, cores por valor).

## 9. Frontend — AI Bridge (Export to Chat)

- [x] 9.1 Criar componente `BuildExporter.tsx` — botão "Enviar para Gojo" no canto inferior do Builder.
- [x] 9.2 Implementar função `serializeBuildToJSON(buildState, computedStats)` em `utils/buildSerializer.ts` — gera o JSON padronizado da build.
- [x] 9.3 Implementar função `buildToReadableText(buildJSON)` — converte JSON em texto legível para o chat (ex: "Arma: Fatalis Zaggespanon | Ataque: 370 | ...").
- [x] 9.4 Ao clicar "Enviar para Gojo", chamar `handleSendMessage` do `ChatContext` com o texto formatado e trocar automaticamente para a aba Chat.
- [x] 9.5 No backend (`chat_service.py`), detectar mensagens com formato de build exportada e injetar contexto adequado para o LLM analisar a build.
- [x] 9.6 Validar que o usuário selecionou pelo menos uma arma antes de permitir a exportação.

## 10. Styling & Polish

- [x] 10.1 Criar/atualizar CSS do Builder com design premium: glassmorphism, gradientes, micro-animações de hover/click.
- [x] 10.2 Responsividade: garantir que o layout de duas colunas colapse para single-column em telas menores.
- [x] 10.3 Adicionar transições suaves ao trocar entre abas (Chat ↔ Builder).
- [x] 10.4 Adicionar ícones do `lucide-react` para tipos de equipamento (Sword, Shield, Helmet, etc.).
- [x] 10.5 Testar fluxo completo: selecionar arma → equipar armadura → encaixar joias → ver EFR → exportar para chat.
