
import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { Message, MonsterIntel as MonsterIntelType, Chat } from '../types';
import * as api from '../services/apiService';

interface ChatContextType {
  messages: Message[];
  chats: Chat[];
  activeChatId: string | null;
  isLoading: boolean;
  monsterIntel: MonsterIntelType | null;
  isSidebarCollapsed: boolean;
  fetchChats: () => Promise<void>;
  handleSelectChat: (id: string) => Promise<void>;
  handleCreateChat: () => Promise<void>;
  handleDeleteChat: (id: string) => Promise<void>;
  handleTogglePin: (id: string) => Promise<void>;
  handleSendMessage: (text: string) => Promise<void>;
  toggleSidebar: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [monsterIntel, setMonsterIntel] = useState<MonsterIntelType | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const handleSelectChat = useCallback(async (id: string) => {
    setActiveChatId(id);
    setIsLoading(true);
    try {
      const history = await api.getHistory(id);
      setMessages(history);
      setMonsterIntel(null);
    } catch (error) {
      console.error("Error loading history:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleCreateChat = useCallback(async () => {
    try {
      const newChat = await api.createChat("Nova Conversa");
      setChats(prev => [newChat, ...prev]);
      setActiveChatId(newChat.id);
      setMessages([]);
      setMonsterIntel(null);
    } catch (error) {
      console.error("Error creating chat:", error);
    }
  }, []);

  const fetchChats = useCallback(async () => {
    try {
      const data = await api.getChats();
      setChats(data);
      if (data.length > 0 && !activeChatId) {
        handleSelectChat(data[0].id);
      } else if (data.length === 0) {
        handleCreateChat();
      }
    } catch (error) {
      console.error("Error fetching chats:", error);
    }
  }, [activeChatId, handleSelectChat, handleCreateChat]);

  const handleDeleteChat = useCallback(async (id: string) => {
    try {
      await api.deleteChat(id);
      setChats(prev => prev.filter(c => c.id !== id));
      if (activeChatId === id) {
        setActiveChatId(null);
        setMessages([]);
      }
    } catch (error) {
      console.error("Error deleting chat:", error);
    }
  }, [activeChatId]);

  const handleTogglePin = useCallback(async (id: string) => {
    try {
      await api.pinChat(id);
      fetchChats();
    } catch (error) {
      console.error("Error pinning chat:", error);
    }
  }, [fetchChats]);

  const handleSendMessage = useCallback(async (text: string) => {
    if (!activeChatId) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const apiData = await api.getChatResponse(text, activeChatId);

      let responseText = "";
      let detectedMonster = null;

      if (typeof apiData === 'string') {
        responseText = apiData;
      } else {
        responseText = apiData.response;
        detectedMonster = apiData.detected_monster;
        fetchChats();
      }

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responseText || "Forgive me, Hunter. I lost my notes.",
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, assistantMsg]);

      if (detectedMonster) {
        const intel = await api.getMonsterIntel(detectedMonster);
        if (intel && intel.weakness) {
          setMonsterIntel({
            ...intel,
            name: detectedMonster.charAt(0).toUpperCase() + detectedMonster.slice(1).toLowerCase(),
            image: intel.image || `https://picsum.photos/seed/${detectedMonster}/800/600`
          });
        }
      }
    } catch (error) {
      console.error(error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "⚠️ Não consegui processar sua mensagem.",
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [activeChatId, fetchChats]);

  const toggleSidebar = useCallback(() => {
    setIsSidebarCollapsed(prev => !prev);
  }, []);

  // Load chats on mount
  useEffect(() => {
    fetchChats();
  }, []);

  // Ctrl+Q handler
  useEffect(() => {
    const handleKeyDown = async (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key.toLowerCase() === 'q') {
        try { await fetch('/shutdown', { method: 'POST' }); } catch (err) { }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <ChatContext.Provider value={{
      messages,
      chats,
      activeChatId,
      isLoading,
      monsterIntel,
      isSidebarCollapsed,
      fetchChats,
      handleSelectChat,
      handleCreateChat,
      handleDeleteChat,
      handleTogglePin,
      handleSendMessage,
      toggleSidebar,
    }}>
      {children}
    </ChatContext.Provider>
  );
};
