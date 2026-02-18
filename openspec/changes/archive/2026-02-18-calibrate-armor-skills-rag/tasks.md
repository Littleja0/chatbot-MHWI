# Tasks: Calibrar Precisão de Armaduras e Skills no RAG

## 1. Refatoração do rag_loader.py (Armaduras)
- [x] 1.1 Modificar `_load_armor` para usar o novo template de "pseudotabela" (chave-valor) para cada peça.
- [x] 1.2 Injetar palavras-chave de metadados (Master Rank, RM, Alfa Plus, α+, Beta Plus, β+) diretamente no texto de cada peça de armadura.
- [x] 1.3 Garantir que os slots de decoração sejam exibidos no formato amigável ao LLM: `Slots: [4, 1, 0]`.
- [x] 1.4 Integrar informações de Bônus de Set de forma clara no cabeçalho do documento do conjunto de armadura.

## 2. Implementação do Reverse Skill Lookup
- [x] 2.1 Criar a função `_load_skill_reverse_lookup` no `rag_loader.py` para agregar fontes de habilidades (armaduras, amuletos, decorações).
- [x] 2.2 Registrar o novo loader no entry point `load_all_documents`.
- [x] 2.3 Formatar os documentos de skill com prefixo "SKILL:" e categorizar fontes por Rank e Tipo de Peça.

## 3. Melhoria na Expansão de Queries (mhw_rag.py)
- [x] 3.1 Atualizar `_expand_queries` para realizar a normalização de símbolos gregos (a+, alpha+ -> α+, etc).
- [x] 3.2 Adicionar lógica de detecção de intenção de busca de skills para gerar sub-queries direcionadas aos novos documentos de reverse lookup.
- [x] 3.3 Garantir redundância de busca para termos de Rank (MR / Master Rank).

## 4. Verificação e Rebuild
- [x] 4.1 Disparar um rebuild completo da base RAG (deletando a pasta `data/storage` ou alterando um XML para triggar o `rag_pipeline`).
- [x] 4.2 Realizar testes manuais com perguntas complexas: "Quais peças de Master Rank dão a skill Ataque?" e "Quais os slots do Elmo Rathalos β+?".
- [x] 4.3 Validar se o chatbot consegue distinguir corretamente entre peças Alfa e Beta no mesmo set.
