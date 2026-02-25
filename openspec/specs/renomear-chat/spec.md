# Spec: renomear-chat

## Purpose
Esta especificação define os requisitos para a funcionalidade de renomear chats manualmente na barra lateral do chatbot, permitindo que o usuário organize suas conversas de forma personalizada.

## Requirements
### Requirement: Edição de Título na Interface
- **GIVEN**: O usuário está com o mouse sobre um item de chat na barra lateral (Sidebar).
- **WHEN**: O usuário clica no ícone de "Renomear" (lápis/edição).
- **THEN**: O texto do título deve ser substituído por um campo de entrada (input) contendo o nome atual.

### Requirement: Persistência da Alteração
- **GIVEN**: O usuário está no modo de edição do título.
- **WHEN**: O usuário pressiona "Enter" ou clica fora do campo (blur).
- **THEN**: O sistema deve enviar uma requisição PATCH para `/chats/{chat_id}/title` com o novo nome e atualizar a interface localmente.

### Requirement: Cancelamento da Edição
- **GIVEN**: O usuário está no modo de edição do título.
- **WHEN**: O usuário pressiona "Esc" ou limpa o campo e sai.
- **THEN**: O título original deve ser restaurado e o modo de edição fechado.

## Acceptance Criteria
- O ícone de renomear aparece ao passar o mouse sobre o chat.
- Pressionar Enter salva o novo título.
- O título é atualizado instantaneamente na barra lateral após o salvamento.
- O backend recebe e persiste o novo título no banco de dados `sessions.db`.
