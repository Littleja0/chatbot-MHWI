
import { useChatContext } from '../contexts/ChatContext';

/**
 * Hook para operações de chat.
 * Simplesmente re-exporta do contexto para uma API mais limpa nos componentes.
 */
export function useChat() {
    const {
        messages,
        isLoading,
        activeChatId,
        handleSendMessage,
    } = useChatContext();

    return {
        messages,
        isLoading,
        activeChatId,
        sendMessage: handleSendMessage,
    };
}

/**
 * Hook para operações de gerenciamento de chats (sidebar).
 */
export function useChatManager() {
    const {
        chats,
        activeChatId,
        isSidebarCollapsed,
        handleSelectChat,
        handleCreateChat,
        handleDeleteChat,
        handleTogglePin,
        handleRenameChat,
        toggleSidebar,
    } = useChatContext();

    return {
        chats,
        activeChatId,
        isSidebarCollapsed,
        selectChat: handleSelectChat,
        createChat: handleCreateChat,
        deleteChat: handleDeleteChat,
        togglePin: handleTogglePin,
        renameChat: handleRenameChat,
        toggleSidebar,
    };
}
