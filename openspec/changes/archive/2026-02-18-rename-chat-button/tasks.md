# Tasks: rename-chat-button

## Arquitetura e API
- [x] 1.1 Adicionar função `updateChatTitle` no `apps/frontend/src/services/apiService.ts`.
- [x] 1.2 Adicionar `handleRenameChat` na interface `ChatContextType` e sua implementação no `ChatProvider` em `ChatContext.tsx`.

## Interface (Frontend)
- [x] 2.1 Adicionar o ícone `Edit2` aos imports de `lucide-react` no `Sidebar.tsx`.
- [x] 2.2 Implementar estados `editingId` e `tempTitle` no componente `Sidebar`.
- [x] 2.3 Criar a função `startEditing` e `submitRename` no `Sidebar.tsx`.
- [x] 2.4 Modificar o JSX do `Sidebar.tsx` para exibir o input de edição e o botão de editar.
- [x] 2.5 Adicionar acessibilidade (foco automático no input e handlers de teclado).

## Verificação e Testes
- [x] 3.1 Verificar se a renomeação persiste após recarregar a página.
- [x] 3.2 Testar o comportamento de cancelamento (tecla Esc).
- [x] 3.3 Validar se o backend responde corretamente às requisições do frontend.
