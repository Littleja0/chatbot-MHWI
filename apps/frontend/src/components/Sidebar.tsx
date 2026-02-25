
import React from 'react';
import { MessageSquare, Pin, Plus, Trash2, PanelLeftClose, PanelLeftOpen, Pencil } from 'lucide-react';
import { Chat } from '../types';

interface SidebarProps {
  chats: Chat[];
  activeChatId: string | null;
  onSelectChat: (id: string) => void;
  onCreateChat: () => void;
  onDeleteChat: (id: string) => void;
  onTogglePin: (id: string) => void;
  onRenameChat: (id: string, title: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  chats,
  activeChatId,
  onSelectChat,
  onCreateChat,
  onDeleteChat,
  onTogglePin,
  onRenameChat,
  isCollapsed,
  onToggleCollapse
}) => {
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [editTitle, setEditTitle] = React.useState("");

  const recentChats = chats.filter(c => !c.is_pinned);
  const pinnedChats = chats.filter(c => c.is_pinned);

  const startEditing = (e: React.MouseEvent, chat: Chat) => {
    e.stopPropagation();
    setEditingId(chat.id);
    setEditTitle(chat.title);
  };

  const handleRename = (id: string) => {
    if (editTitle.trim()) {
      onRenameChat(id, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent, id: string) => {
    if (e.key === 'Enter') handleRename(id);
    if (e.key === 'Escape') setEditingId(null);
  };

  return (
    <div className={`${isCollapsed ? 'w-16' : 'w-64'} bg-[#141414] border-r border-[#2a2a2a] flex flex-col h-full overflow-hidden transition-all duration-300 ease-in-out relative`}>
      <div className={`p-4 flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'} border-b border-[#2a2a2a] min-h-[65px]`}>
        <div className="flex items-center gap-2 overflow-hidden">
          <div className="w-8 h-8 bg-[#3d3d3d] rounded flex-shrink-0 flex items-center justify-center">
            <span className="text-sm font-bold cinzel-font text-white">MH</span>
          </div>
          {!isCollapsed && <h1 className="text-lg cinzel-font font-bold tracking-tight text-white truncate">MHW:I AI Hub</h1>}
        </div>
        <button
          onClick={onToggleCollapse}
          className="p-1.5 hover:bg-[#2a2a2a] rounded-lg transition-colors text-gray-400 hover:text-white"
          title={isCollapsed ? "Expandir" : "Recolher"}
        >
          {isCollapsed ? <PanelLeftOpen size={20} /> : <PanelLeftClose size={20} />}
        </button>
      </div>

      <div className={`flex-1 overflow-y-auto ${isCollapsed ? 'px-1' : 'px-2'} py-4 space-y-6 scrollbar-thin`}>
        <section>
          <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'} px-2 mb-2 text-xs font-semibold uppercase text-gray-500 tracking-wider`}>
            {!isCollapsed && <span>Recent Chats</span>}
            <button
              onClick={onCreateChat}
              className="hover:text-white transition-colors p-1"
              title="Novo Chat"
            >
              <Plus size={isCollapsed ? 18 : 14} />
            </button>
          </div>
          <ul className="space-y-1">
            {recentChats.map((chat) => (
              <li
                key={chat.id}
                onClick={() => onSelectChat(chat.id)}
                className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'} gap-2 px-3 py-2 text-sm rounded cursor-pointer transition-all group ${activeChatId === chat.id
                  ? 'bg-[#222] text-white border border-[#333]'
                  : 'text-gray-400 hover:bg-[#1a1a1a] hover:text-gray-200'
                  }`}
                title={isCollapsed ? chat.title : ""}
              >
                <div className="flex items-center gap-2 truncate flex-1">
                  <MessageSquare size={isCollapsed ? 18 : 14} className="opacity-60 flex-shrink-0" />
                  {!isCollapsed && (
                    editingId === chat.id ? (
                      <input
                        autoFocus
                        className="bg-[#333] border-none text-white text-xs px-1 py-0.5 rounded w-full outline-none focus:ring-1 focus:ring-blue-500"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onBlur={() => handleRename(chat.id)}
                        onKeyDown={(e) => handleKeyDown(e, chat.id)}
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <span className="truncate">{chat.title}</span>
                    )
                  )}
                </div>
                {!isCollapsed && (
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => startEditing(e, chat)}
                      className="p-1 hover:text-blue-400 transition-colors"
                      title="Renomear"
                    >
                      <Pencil size={12} />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); onTogglePin(chat.id); }}
                      className="p-1 hover:text-yellow-500 transition-colors"
                    >
                      <Pin size={12} className="rotate-45" />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); onDeleteChat(chat.id); }}
                      className="p-1 hover:text-red-500 transition-colors"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </section>

        {pinnedChats.length > 0 && (
          <section>
            <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'} px-2 mb-2 text-xs font-semibold uppercase text-gray-500 tracking-wider`}>
              {!isCollapsed && <span>Pinned Guides</span>}
            </div>
            <ul className="space-y-1">
              {pinnedChats.map((chat) => (
                <li
                  key={chat.id}
                  onClick={() => onSelectChat(chat.id)}
                  className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'} gap-2 px-3 py-2 text-sm rounded cursor-pointer transition-all group ${activeChatId === chat.id
                    ? 'bg-[#222] text-white border border-[#333]'
                    : 'text-gray-400 hover:bg-[#1a1a1a] hover:text-gray-200'
                    }`}
                  title={isCollapsed ? chat.title : ""}
                >
                  <div className="flex items-center gap-2 truncate flex-1">
                    <Pin size={isCollapsed ? 18 : 14} className="opacity-60 rotate-45 text-yellow-600 flex-shrink-0" />
                    {!isCollapsed && (
                      editingId === chat.id ? (
                        <input
                          autoFocus
                          className="bg-[#333] border-none text-white text-xs px-1 py-0.5 rounded w-full outline-none focus:ring-1 focus:ring-blue-500"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onBlur={() => handleRename(chat.id)}
                          onKeyDown={(e) => handleKeyDown(e, chat.id)}
                          onClick={(e) => e.stopPropagation()}
                        />
                      ) : (
                        <span className="truncate underline decoration-gray-700 underline-offset-4">{chat.title}</span>
                      )
                    )}
                  </div>
                  {!isCollapsed && (
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => startEditing(e, chat)}
                        className="p-1 hover:text-blue-400 transition-colors"
                        title="Renomear"
                      >
                        <Pencil size={12} />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); onTogglePin(chat.id); }}
                        className="p-1 hover:text-yellow-500 transition-colors"
                      >
                        <Pin size={12} className="rotate-0" />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); onDeleteChat(chat.id); }}
                        className="p-1 hover:text-red-500 transition-colors"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>    </div>
  );
};

export default Sidebar;
