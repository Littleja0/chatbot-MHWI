
import React, { useState, useCallback, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatArea from './components/ChatArea';
import MonsterIntel from './components/MonsterIntel';
import InputBar from './components/InputBar';
import { Message, MonsterIntel as MonsterIntelType, Chat } from './types';
import * as api from './services/apiService';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [monsterIntel, setMonsterIntel] = useState<MonsterIntelType | null>(null);

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // Carregar lista de chats ao iniciar
  const fetchChats = useCallback(async () => {
    try {
      const data = await api.getChats();
      setChats(data);
      // Se tiver chats e nenhum estiver ativo, seleciona o primeiro
      if (data.length > 0 && !activeChatId) {
        handleSelectChat(data[0].id);
      } else if (data.length === 0) {
        handleCreateChat();
      }
    } catch (error) {
      console.error("Error fetching chats:", error);
    }
  }, [activeChatId]);

  useEffect(() => {
    fetchChats();
  }, []);

  const handleSelectChat = async (id: string) => {
    setActiveChatId(id);
    setIsLoading(true);
    try {
      const history = await api.getHistory(id);
      setMessages(history);
      setMonsterIntel(null); // Limpar intel ao trocar de chat
    } catch (error) {
      console.error("Error loading history:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateChat = async () => {
    try {
      const newChat = await api.createChat("Nova Conversa");
      setChats(prev => [newChat, ...prev]);
      setActiveChatId(newChat.id);
      setMessages([]);
      setMonsterIntel(null);
    } catch (error) {
      console.error("Error creating chat:", error);
    }
  };

  const handleDeleteChat = async (id: string) => {
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
  };

  const handleTogglePin = async (id: string) => {
    try {
      await api.pinChat(id);
      fetchChats(); // Recarregar para ordenar
    } catch (error) {
      console.error("Error pinning chat:", error);
    }
  };

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
        // Se o backend retornou um novo título (primeira mensagem), atualizamos a lista local
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

  // Bind para fechar (Ctrl+Q)
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
    <div className="flex h-screen bg-black text-gray-100 overflow-hidden">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onCreateChat={handleCreateChat}
        onDeleteChat={handleDeleteChat}
        onTogglePin={handleTogglePin}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      <main className="flex-1 flex flex-col relative overflow-hidden">
        <Header />

        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 flex flex-col">
            <ChatArea messages={messages} isLoading={isLoading} />
            <InputBar onSendMessage={handleSendMessage} disabled={isLoading || !activeChatId} />
          </div>

          {monsterIntel && <MonsterIntel {...monsterIntel} />}
        </div>
      </main>
    </div>

  );
};

export default App;
