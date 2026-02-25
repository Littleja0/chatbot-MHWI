
import React, { useState, useEffect } from 'react';
import { ChatProvider } from './contexts/ChatContext';
import { BuildProvider } from './contexts/BuildContext';
import { useChatManager } from './hooks/useChat';
import { useMonsterData } from './hooks/useMonsterData';
import { useChat } from './hooks/useChat';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatArea from './components/ChatArea';
import MonsterIntel from './components/MonsterIntel';
import InputBar from './components/InputBar';
import BuilderView from './components/builder/BuilderView';
import './App.css';

/**
 * Layout principal — agora é apenas UI, sem lógica de negócio.
 */
const AppLayout: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('chat');

  // Listen for tab switch events (e.g. from BuildExporter)
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail) setActiveTab(detail);
    };
    window.addEventListener('switch-tab', handler);
    return () => window.removeEventListener('switch-tab', handler);
  }, []);

  const {
    chats, activeChatId, isSidebarCollapsed,
    selectChat, createChat, deleteChat, togglePin, toggleSidebar
  } = useChatManager();

  const { messages, isLoading, sendMessage } = useChat();
  const monsterIntel = useMonsterData();

  return (
    <div className="app-container">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={selectChat}
        onCreateChat={createChat}
        onDeleteChat={deleteChat}
        onTogglePin={togglePin}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={toggleSidebar}
      />

      <main className="flex-1 flex flex-col relative overflow-hidden">
        <Header activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Chat View — hidden via CSS to preserve state */}
        <div
          className="flex-1 flex flex-col overflow-hidden"
          style={{
            display: activeTab === 'chat' ? 'flex' : 'none',
            opacity: activeTab === 'chat' ? 1 : 0,
            pointerEvents: activeTab === 'chat' ? 'auto' : 'none',
            animation: activeTab === 'chat' ? 'tabFadeIn 0.2s ease' : undefined
          }}
        >
          <div className="flex-1 flex flex-col overflow-hidden">
            <ChatArea messages={messages} isLoading={isLoading} />
            <InputBar onSendMessage={sendMessage} disabled={isLoading || !activeChatId} />
          </div>

          {monsterIntel && activeTab === 'chat' && <MonsterIntel {...monsterIntel} />}
        </div>

        {/* Builder View — hidden via CSS to preserve state */}
        <div
          className="flex-1 flex flex-col overflow-hidden"
          style={{
            display: activeTab === 'builds' ? 'flex' : 'none',
            opacity: activeTab === 'builds' ? 1 : 0,
            pointerEvents: activeTab === 'builds' ? 'auto' : 'none',
            animation: activeTab === 'builds' ? 'tabFadeIn 0.2s ease' : undefined
          }}
        >
          <BuilderView />
        </div>
      </main>
    </div>
  );
};

/**
 * App root — envolve tudo com os providers.
 */
const App: React.FC = () => {
  return (
    <ChatProvider>
      <BuildProvider>
        <AppLayout />
      </BuildProvider>
    </ChatProvider>
  );
};

export default App;
