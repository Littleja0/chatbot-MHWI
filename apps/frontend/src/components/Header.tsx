
import React from 'react';
import { MessageSquare, Sword, ShieldAlert, BookOpen, User } from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

const Header: React.FC<HeaderProps> = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'chat', label: 'Chat', icon: <MessageSquare size={18} /> },
    { id: 'builds', label: 'Builds', icon: <Sword size={18} /> },
    { id: 'monsters', label: 'Monsters', icon: <ShieldAlert size={18} />, disabled: true },
    { id: 'guides', label: 'Guides', icon: <BookOpen size={18} />, disabled: true },
  ];

  return (
    <header className="h-14 bg-[#111] border-b border-[#2a2a2a] flex items-center justify-between px-6 shadow-xl z-[9999] relative">
      <div className="flex items-center gap-1 h-full">
        {tabs.map((tab) => (
          <a
            key={tab.id}
            href={`#${tab.id}`}
            onClick={(e) => {
              e.preventDefault();
              if (!tab.disabled) {
                onTabChange(tab.id);
              }
            }}
            className={`flex items-center gap-2 px-6 h-full transition-all relative border-b-2 no-underline ${activeTab === tab.id
              ? 'bg-[#222] text-white border-blue-500'
              : tab.disabled
                ? 'text-gray-600 border-transparent cursor-not-allowed opacity-50'
                : 'text-gray-400 border-transparent hover:text-gray-200 hover:bg-[#181818] cursor-pointer'
              }`}
          >
            {tab.icon}
            <span className="text-sm font-medium">{tab.label}</span>
          </a>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <div className="p-2 text-gray-400 hover:text-white transition-colors cursor-pointer">
          <User size={20} className="rounded-full border border-gray-600 p-0.5" />
        </div>
      </div>
    </header>
  );
};

export default Header;
