
import React from 'react';
import { ChatProvider } from './contexts/ChatContext';
import { useChatManager } from './hooks/useChat';
import { useMonsterData } from './hooks/useMonsterData';
import { useChat } from './hooks/useChat';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatArea from './components/ChatArea';
import MonsterIntel from './components/MonsterIntel';
import InputBar from './components/InputBar';

/**
 * Layout principal — agora é apenas UI, sem lógica de negócio.
 */
const AppLayout: React.FC = () => {
  const {
    chats, activeChatId, isSidebarCollapsed,
    selectChat, createChat, deleteChat, togglePin, toggleSidebar
  } = useChatManager();

  const { messages, isLoading, sendMessage } = useChat();
  const monsterIntel = useMonsterData();

  return (
    <div className="flex h-screen bg-black text-gray-100 overflow-hidden">
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
        <Header />

        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 flex flex-col">
            <ChatArea messages={messages} isLoading={isLoading} />
            <InputBar onSendMessage={sendMessage} disabled={isLoading || !activeChatId} />
          </div>

          {monsterIntel && <MonsterIntel {...monsterIntel} />}
        </div>
      </main>
    </div>
  );
};

/**
 * App root — envolve tudo com o provider.
 */
const App: React.FC = () => {
  return (
    <ChatProvider>
      <AppLayout />
    </ChatProvider>
  );
};

export default App;
