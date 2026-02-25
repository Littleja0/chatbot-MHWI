# Design: rename-chat-button

## Context
O sistema atual permite criar, deletar e fixar chats. Os títulos são gerados automaticamente ou permanecem como "Nova Conversa". O backend já possui suporte para atualização de título via `PATCH /chats/{chat_id}/title`.

## Goals
- Adicionar um botão de renomear em cada item de chat na `Sidebar`.
- Implementar a lógica de edição inline no frontend.
- Integrar com o endpoint de backend existente.

## Technical Decisions

### Frontend
1. **ChatContext**: 
   - Adicionar `handleRenameChat(id: string, title: string)` que chama `api.updateChatTitle(id, title)` e atualiza a lista de chats localmente (ou chama `fetchChats`).
2. **apiService**:
   - Adicionar a função `updateChatTitle(id, title)` para realizar a chamada `PATCH`.
3. **Sidebar Component**:
   - Adicionar estado local `editingId` e `tempTitle`.
   - Modificar a renderização do chat para mostrar um `<input>` quando `chat.id === editingId`.
   - Adicionar botão com o ícone `Edit2` da biblioteca `lucide-react`.
   - Implementar handlers para `onKeyDown` (Enter/Esc) e `onBlur`.

### Backend
- Nenhuma mudança necessária no backend, apenas verificação de que o endpoint está funcionando conforme o esperado.

## UI/UX
- O ícone de edição aparecerá ao lado dos botões de Pin e Lixeira quando o usuário fizer hover no item do chat.
- Ao clicar em editar, o texto vira um input com foco automático.
- Visual clean, mantendo a consistência com o design escuro atual.

## Risks / Trade-offs
- **Concorrência**: Se o usuário renomear enquanto uma mensagem está sendo processada, pode haver um conflito na atualização do título se o backend tentar gerar um título automático simultaneamente. Resolveremos isso garantindo que a renomeação manual tenha precedência ou desativando a geração automática após a primeira renomeação manual (desnecessário por enquanto, basta o frontend atualizar).
