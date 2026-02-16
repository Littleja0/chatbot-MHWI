# Design: Arquitetura Sem Memória (Pure RAG)

## Visão Geral
A remoção do `memory_reader.py` simplifica drasticamente o fluxo de dados. A IA deixará de receber o bloco `═══ DADOS EM TEMPO REAL ═══`.

## Mudanças Arquiteturais

### 1. Eliminação de Dependências
- Deletar `backend/memory_reader.py`.
- Remover `pymem` do ambiente (via documentação/instruções futuras).

### 2. Limpeza do `backend/main.py`
- Remover imports de `memory_reader`.
- Deletar todas as rotas prefixadas com `/memory/`.
- Deletar a rota `/overlay/damage`.
- Simplificar a função `chat` para remover a injeção de `memory_context`.

### 3. Ajuste do Prompt de Sistema
- O "Middleware Anti-Hallucination" no `main.py` deve parar de mencionar dados de memória.
- Focar na personalidade do Satoru Gojo baseada nos dados do RAG e no Perfil do usuário (que permanece no `sessions.db`).

### 4. Interface (UI)
- O frontend deve remover menus ou botões de "Connect to Game".
- O botão de "Sync Save" (que já estava como placeholder) será removido ou redirecionado para o perfil manual.

## Diagrama de Fluxo (Simplificado)
```ascii
[Usuário] ───▶ [Chat API] ───▶ [RAG Search] ───▶ [LLM (Gojo)] ───▶ [Resposta]
                  │               ▲
                  └───────────────┘
               (Usa Profile Manual)
```
