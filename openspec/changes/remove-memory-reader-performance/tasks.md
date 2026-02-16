# Tarefas: Remoção do Memory Reader

## Fase 1: Limpeza de Código [status: done]
- [x] Deletar `backend/memory_reader.py`
- [x] Deletar `backend/overlay_damage.html`
- [x] Remover imports de `memory_reader` em `backend/main.py`
- [x] Deletar rotas `/memory/*` em `backend/main.py`
- [x] Deletar rota `/overlay/damage` em `backend/main.py`
- [x] Remover lógica de `memory_context` na função `chat` do `backend/main.py`

## Fase 2: Refatoração do Prompt [status: done]
- [x] Atualizar `anti_hallucination_middleware` para remover referências à memória
- [x] Ajustar instruções de personalidade para focar no Perfil Manual e RAG

## Fase 3: Verificação [status: done]
- [x] Validar que o servidor inicia sem erros de importação
- [x] Testar uma conversa no chat para garantir que a IA responde sem tentar ler a memória
- [x] Verificar se as rotas removidas retornam 404 corretamente
