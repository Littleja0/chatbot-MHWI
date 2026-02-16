
import React from 'react';
import { MessageSquare, Sword, ShieldAlert, BookOpen, User } from 'lucide-react';

const Header: React.FC = () => {
  const tabs = [
    { id: 'chat', label: 'Chat', icon: <MessageSquare size={18} />, active: true },
    { id: 'builds', label: 'Builds', icon: <Sword size={18} />, active: false },
    { id: 'monsters', label: 'Monsters', icon: <ShieldAlert size={18} />, active: false },
    { id: 'guides', label: 'Guides', icon: <BookOpen size={18} />, active: false },
  ];

  return (
    <header className="h-14 bg-[#111] border-b border-[#2a2a2a] flex items-center justify-between px-6 shadow-xl z-10">
      <div className="flex items-center gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`flex items-center gap-2 px-6 h-14 transition-all relative border-b-2 ${
              tab.active 
                ? 'bg-[#1a1a1a] text-white border-[#5a5a5a]' 
                : 'text-gray-400 border-transparent hover:text-gray-200 hover:bg-[#151515]'
            }`}
          >
            {tab.icon}
            <span className="text-sm font-medium">{tab.label}</span>
          </button>
        ))}
      </div>
      
      <div className="flex items-center gap-4">
        <button className="p-2 text-gray-400 hover:text-white transition-colors">
          <User size={20} className="rounded-full border border-gray-600 p-0.5" />
        </button>
      </div>
    </header>
  );
};

export default Header;
