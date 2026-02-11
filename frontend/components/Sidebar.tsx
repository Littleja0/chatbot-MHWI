
import React from 'react';
import { MessageSquare, Pin, Plus } from 'lucide-react';

const Sidebar: React.FC = () => {
  const recentChats = [
    "Dual Blades Build for Safi'jiiva",
    "Alatreon Strategy",
    "Nest sorter Build for MHW:B...",
    "Alatreon Information Tips"
  ];

  const pinnedGuides = [
    "Fatalis Strategy",
    "Alatreon Elemental Tips",
    "Alatreon Concept Elements",
    "Pinned Guide: Strategy"
  ];

  return (
    <div className="w-64 bg-[#141414] border-r border-[#2a2a2a] flex flex-col h-full overflow-hidden">
      <div className="p-4 flex items-center gap-2 border-b border-[#2a2a2a]">
        <div className="w-8 h-8 bg-[#3d3d3d] rounded flex items-center justify-center">
           <span className="text-sm font-bold cinzel-font">MH</span>
        </div>
        <h1 className="text-lg cinzel-font font-bold tracking-tight">MHW:I AI Hub</h1>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-4 space-y-6">
        <section>
          <div className="flex items-center justify-between px-2 mb-2 text-xs font-semibold uppercase text-gray-500 tracking-wider">
            <span>Recent Chats</span>
            <button className="hover:text-white transition-colors"><Plus size={14} /></button>
          </div>
          <ul className="space-y-1">
            {recentChats.map((chat, idx) => (
              <li key={idx} className={`flex items-center gap-2 px-3 py-2 text-sm rounded cursor-pointer transition-colors group ${idx === 0 ? 'bg-[#222] text-white border border-[#333]' : 'text-gray-400 hover:bg-[#1a1a1a] hover:text-gray-200'}`}>
                <MessageSquare size={14} className="opacity-60" />
                <span className="truncate">{chat}</span>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <div className="flex items-center justify-between px-2 mb-2 text-xs font-semibold uppercase text-gray-500 tracking-wider">
            <span>Pinned Guides</span>
            <button className="hover:text-white transition-colors"><Plus size={14} /></button>
          </div>
          <ul className="space-y-1">
            {pinnedGuides.map((guide, idx) => (
              <li key={idx} className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:bg-[#1a1a1a] hover:text-gray-200 cursor-pointer transition-colors">
                <Pin size={14} className="opacity-60 rotate-45" />
                <span className="truncate underline decoration-gray-700 underline-offset-4">{guide}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
};

export default Sidebar;
