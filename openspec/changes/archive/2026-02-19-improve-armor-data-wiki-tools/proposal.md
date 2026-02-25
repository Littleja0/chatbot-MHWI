# Proposta: Dados Precisos via Wiki e Tool Calling (LR/HR/MR)

## Problema
O sistema atual de RAG (Retrieval-Augmented Generation) para armaduras e armas apresenta imprecisões críticas nos slots, níveis de habilidades e filtragem de Rank. O chatbot frequentemente "alucina" informações técnicas ou mistura dados de Master Rank com High/Low Rank, resultando em builds impossíveis de construir no jogo.

## Objetivo
Transformar o `chatbot-MHWI` em um guia técnico infalível através de:
1. **Extração Estruturada (Wiki):** Criar scrapers para capturar dados verificados da Wiki Fextralife para todos os Ranks (Low Rank, High Rank e Master Rank).
2. **Consultas Determinísticas (Tool Calling):** Implementar ferramentas de consulta no backend que acessam diretamente o banco de dados SQL em vez de confiar apenas em busca vetorial.
3. **Filtro de Perfil:** Garantir que o bot respeite o Rank do jogador (MR/HR/LR) e seu inventário de joias ao sugerir equipamentos.

## Escopo
- **Coleção de Dados:** 
  - Scrappers para Armaduras (LR, HR, MR).
  - Scrappers para Armas (Todas as categorias, todos os Ranks).
- **Banco de Dados:** Ativação/População das tabelas `armor`, `weapon`, `armor_skill`, e `weapon_skill` no `mhw.db` com dados da Wiki.
- **Backend:** 
  - Implementação de funções de busca estruturadas no `chat_service.py`.
  - Integração com o sistema de `Function Calling` da LLM.
- **Frontend:** Exibição clara de builds com distinção de slots e raridade.

## Critérios de Sucesso
- O bot retornar exatamente os mesmos slots e skills mostrados na Wiki para qualquer peça solicitada.
- O bot não sugerir peças de MR para um usuário que se identificou no Rank LR/HR.
- O bot utilizar o inventário de joias cadastrado para preencher os slots das builds sugeridas.

## Capacidades Impactadas
- `core-knowledge-base`: Substituição dos XMLs extraídos por dados SQL estruturados.
- `chat-service`: Adição de ferramentas de busca.
- `user-profile`: Melhor uso dos dados de Rank e Joias.
