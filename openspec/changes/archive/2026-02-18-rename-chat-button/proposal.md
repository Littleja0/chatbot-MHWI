# Proposal: rename-chat-button

## Summary
Atualmente, os chats no sidebar são nomeados automaticamente com base na primeira mensagem do usuário ou mantêm um título genérico. O usuário deseja ter controle sobre esses nomes para melhor organização de suas conversas e guias salvos. Esta proposta visa adicionar a capacidade de renomear manualmente cada chat através de um botão dedicado na interface.

## New Capabilities
- **renomear-chat**: Permite ao usuário editar o título de um chat existente na barra lateral. Isso inclui a interface de edição (input de texto) e a persistência da mudança no banco de dados através da API existente.

## Impacted Capabilities
- **gerenciamento-de-sidebar**: A barra lateral (Sidebar) agora deve suportar um modo de edição para o título do chat ou um modal/prompt para renomear.
- **persistência-de-chat**: Embora a API já possua o endpoint `/chats/{chat_id}/title`, garantiremos que o frontend o utilize corretamente e trate atualizações de estado local.

## Impact
- **Frontend**: `Sidebar.tsx` será modificado para incluir o ícone de renomear e a lógica de estado para alternar entre visualização e edição (ou abrir um prompt).
- **Backend**: Nenhuma mudança estrutural necessária, pois o endpoint `PATCH /chats/{chat_id}/title` já está implementado em `chat.py`.
- **UX**: Melhora na organização pessoal do usuário, permitindo nomes claros como "Build Dragão Negro" ou "Farm de Decorações".
