# Spec: Build AI Bridge

## Purpose
Define a integração bidirecional entre o Builder interativo e o Chat (Gojo), permitindo exportar builds para análise pela IA e receber sugestões diretamente no contexto do Builder.

## Requirements

### Requirement: Export Build to Chat
O usuário deve poder enviar o estado atual do Builder como uma mensagem estruturada para o Chat.

#### Scenario: Exportar Build Completa
- **WHEN** o usuário clica no botão "Enviar para Gojo" no Builder.
- **THEN** o sistema gera um resumo textual estruturado da build contendo:
  - Arma (nome, ataque, afinidade, elemento, aumentos).
  - Armaduras (5 peças com skills nativas).
  - Amuleto (skill e nível).
  - Joias equipadas (agrupadas por peça).
  - Despertares de Safi (se aplicável).
  - Custom Upgrades de Kulve (se aplicável).
  - Skills totais ativas.
  - EFR calculado, Afinidade efetiva.
- **AND** esse resumo é enviado como mensagem do usuário no chat ativo.
- **AND** a view muda automaticamente para a aba "Chat" para o usuário ver a resposta.

#### Scenario: Build Incompleta
- **WHEN** o usuário tenta exportar uma build sem arma selecionada.
- **THEN** exibir um aviso: "Selecione pelo menos uma arma antes de enviar para análise."

### Requirement: AI Build Analysis
Quando o Gojo recebe uma build exportada, deve analisar e fornecer feedback contextualizado.

#### Scenario: Análise Automática
- **GIVEN** uma mensagem de build exportada chega no chat.
- **THEN** o backend deve reconhecer o formato de build e injetar contexto adicional (dados SQL verificados) antes de enviar ao LLM.
- **AND** o LLM deve responder com análise de:
  - Skills desperdiçadas ou subótimas.
  - Sugestões de troca (ex: "Troque a joia X por Y para ganhar +5% Affinity").
  - Avaliação do EFR em relação a builds meta.

### Requirement: Build Format JSON
O Builder deve gerar um JSON serializado padronizado que o backend consegue parsear.

#### Scenario: Formato de Exportação
- **GIVEN** uma build completa no Builder.
- **THEN** o JSON exportado deve seguir o schema:
```json
{
  "weapon": { "name": "...", "attack": 0, "affinity": 0, "element": null, "slots": [], "augments": [], "safiAwakenings": [], "customUpgrades": [] },
  "armor": {
    "head": { "name": "...", "skills": [], "slots": [] },
    "chest": { "name": "...", "skills": [], "slots": [] },
    "arms": { "name": "...", "skills": [], "slots": [] },
    "waist": { "name": "...", "skills": [], "slots": [] },
    "legs": { "name": "...", "skills": [], "slots": [] }
  },
  "charm": { "name": "...", "skills": [] },
  "decorations": { "head": [], "chest": [], "arms": [], "waist": [], "legs": [], "weapon": [] },
  "computed": { "trueRaw": 0, "efr": 0, "affinity": 0, "element": 0, "activeSkills": [], "setBonuses": [] }
}
```

### Requirement: Prompt Engineering para Build Analysis
O backend deve formatar o JSON de build em um prompt optimizado para o LLM.

#### Scenario: Prompt Injection
- **GIVEN** um JSON de build recebido via chat.
- **THEN** o backend deve converter para texto legível e adicionar instruções como:
  - "Analise esta build de MHW:I. Verifique se há skills desperdiçadas, afinidade sub-100%, e sugira otimizações mantendo o estilo de jogo do caçador."
- **AND** o prompt deve incluir os dados SQL verificados das peças mencionadas.
