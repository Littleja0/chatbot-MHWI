# Change Proposal: Interactive Build Builder

## Why

Atualmente, o chatbot MHW:I funciona exclusivamente como um assistente conversacional: o usuário pergunta sobre builds e a IA responde em texto Markdown. Porém, o "theorycrafting" de Monster Hunter World é uma atividade **visual e interativa** — caçadores precisam ver os números mudando em tempo real ao trocar uma peça, encaixar uma joia ou escolher um despertar de Safi'jiiva.

Ferramentas como o **Dauntless Builder** e o **Honey Hunter World** provaram que uma interface de montagem de build com feedback instantâneo de estatísticas é o formato ideal para esse tipo de dado. Nosso app já possui toda a base de dados necessária (mhw.db com armaduras, armas, skills e slots), mas não expõe essa informação de forma interativa.

Esta change introduz uma **segunda view principal** (acessível pela aba "Builds" no Header, que já existe mas está inativa) com um construtor de builds completo, incluindo cálculo de dano efetivo (EFR) em tempo real.

## Scope

- **Frontend (`apps/frontend`)**: Nova view "Builder" com componentes de seleção de equipamento, joias e painel de estatísticas.
- **Backend (`apps/backend`)**: Novos endpoints para servir listas completas de equipamentos, joias, skills e set bonuses para popular os dropdowns/seletores do Builder.
- **Engine de Cálculo**: Módulo de cálculo de EFR (Effective Raw) no frontend que processa ataque, afinidade, multiplicadores de afiação, bônus de skills e aumentos.

## Capabilities

- `build-equipment-grid`: Interface visual de seleção de equipamento (Arma, Elmo, Peito, Braços, Cintura, Pernas, Amuleto) com slots de decoração interativos e regra de compatibilidade de tiers (1-4).
- `build-stats-engine`: Motor de cálculo de dano em tempo real (EFR, Afinidade efetiva, Elemento efetivo) considerando skills ativas, aumentos de arma, despertares de Safi'jiiva e Custom Upgrades de Kulve Taroth.
- `build-skills-summary`: Painel lateral de habilidades ativas com barras de progresso segmentadas, suporte a Dynamic Caps (Skill Secrets) e seção de Set Bonuses.
- `build-ai-bridge`: Integração bidirecional entre o Builder e o Chat — exportar build para análise do Gojo, e a IA pode sugerir builds que abrem diretamente no Builder.

## Impacted Capabilities

- `frontend-structure`: O sistema de navegação do Header precisa suportar troca de views (Chat ↔ Builder) com preservação de estado.
- `backend-core`: Novos endpoints de API serão adicionados para servir dados de equipamento completos (com slots, skills, set bonuses) de forma paginada/filtrável.

## Impact

- **Frontend**: Adição de ~5-8 novos componentes (BuilderView, EquipmentSlot, DecorationPicker, SkillBar, StatsPanel, WeaponCustomizer, SetBonusCard, BuildExporter).
- **Backend**: 3-4 novos endpoints REST (`/equipment/armor`, `/equipment/weapons`, `/equipment/decorations`, `/equipment/set-bonuses`).
- **Estado**: Novo contexto React (BuildContext) para gerenciar o estado da build atual, separado do ChatContext existente.
- **Banco de Dados**: Nenhuma alteração no schema do mhw.db — os dados já existem, apenas precisam de queries otimizadas para o Builder.
