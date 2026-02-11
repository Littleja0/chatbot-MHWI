
import React, { useState, useCallback, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatArea from './components/ChatArea';
import MonsterIntel from './components/MonsterIntel';
import InputBar from './components/InputBar';
import { Message, MonsterIntel as MonsterIntelType } from './types';
import { getChatResponse, getMonsterIntel } from './services/apiService';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [monsterIntel, setMonsterIntel] = useState<MonsterIntelType | null>(null);

  const handleSendMessage = useCallback(async (text: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const history = messages.map(m => ({
        role: m.role === 'user' ? 'user' as const : 'model' as const,
        parts: [{ text: m.content }]
      }));

      const apiData = await getChatResponse(text, history);

      let responseText = "";
      let detectedMonster = null;

      if (typeof apiData === 'string') {
        responseText = apiData;
      } else {
        responseText = apiData.response;
        detectedMonster = apiData.detected_monster;
      }

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responseText || "Forgive me, Hunter. I lost my notes.",
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, assistantMsg]);

      // Update monster intel if backend detected a monster
      if (detectedMonster) {
        // Only update if it's different or just always update to be safe
        const intel = await getMonsterIntel(detectedMonster);
        if (intel && intel.weakness) {
          setMonsterIntel({
            name: detectedMonster.charAt(0).toUpperCase() + detectedMonster.slice(1).toLowerCase(), // Capitalize first letter just in case
            weakness: intel.weakness,
            resistances: intel.resistances,
            breakableParts: intel.breakableParts,
            rewards: intel.rewards,
            image: intel.image || `https://picsum.photos/seed/${detectedMonster}/800/600`
          });
        }
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  }, [messages]);

  return (
    <div className="flex h-screen bg-black text-gray-100 overflow-hidden select-none">
      <Sidebar />

      <main className="flex-1 flex flex-col relative overflow-hidden">
        <Header />

        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 flex flex-col">
            <ChatArea messages={messages} isLoading={isLoading} />
            <InputBar onSendMessage={handleSendMessage} disabled={isLoading} />
          </div>

          {monsterIntel && <MonsterIntel {...monsterIntel} />}
        </div>
      </main>
    </div>
  );
};

export default App;
