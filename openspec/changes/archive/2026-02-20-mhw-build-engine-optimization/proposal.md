# Proposal: MHW Build Engine Optimization

## Context
Atualmente, o chatbot de Monster Hunter World Iceborne (persona Satoru Gojo) apresenta inconsistências ao sugerir builds. O modelo de linguagem (LLM) frequentemente alucina a quantidade de slots das peças de armadura, os níveis máximos das habilidades (caps) e a compatibilidade de joias (níveis 1 a 4). Além disso, não há uma lógica determinística para incluir o Amuleto (Charm) e bônus de conjunto (Set Bonuses) na somatória final, resultando em sugestões matematicamente impossíveis no jogo.

## Goals
- **Precisão Determinística:** Validar cada peça de armadura e joia diretamente via consulta ao banco de dados `mhw.db`.
- **Gestão de Slots:** Garantir que joias sugeridas caibam nos slots reais (ex: não sugerir joia nível 4 em slot nível 2).
- **Cálculo de Habilidades:** Somar automaticamente habilidades nativas da armadura, joias e amuleto, respeitando os níveis máximos.
- **Lógica de Substituição:** Oferecer joias substitutas ("RNG Friendly") para joias extremamente raras (Rarity 11/12).
- **Suporte a Amuletos:** Incluir o amuleto ideal como peça central da build.
- **Detecção de Set Bonuses:** Identificar e listar bônus de conjunto ativos (ex: Master's Touch).

## Project Structure
- `apps/backend/src/core/mhw/mhw_tools.py`: Onde as novas funções de cálculo e validação serão implementadas.
- `apps/backend/src/services/chat_service.py`: Ajuste no prompt do sistema e na orquestração para utilizar a nova lógica de build.
- `data/mhw.db`: Fonte de verdade para os dados técnicos.

## Affected Capabilities
- `build-validation`: Nova capacidade para validar e otimizar builds sugeridas pelo LLM.
- `jewel-substitution`: Capacidade de mapear joias ideais versus substitutos viáveis.

## Impact
- **API MHW_TOOLS:** A ferramenta `search_equipment` será refinada e possivelmente complementada por uma nova ferramenta `validate_build`.
- **Prompt do Sistema:** Instruções mais rígidas sobre como utilizar as ferramentas para evitar "chutes" matemáticos.
- **User Experience:** Respostas mais confiáveis e úteis, especialmente para jogadores que ainda não possuem todas as joias raras do jogo.
