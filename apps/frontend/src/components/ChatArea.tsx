
import React, { useRef, useEffect } from 'react';
import { Message } from '../types';
import { User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import gojoImage from '../assets/gojo.jpeg';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
}

const ChatArea: React.FC<ChatAreaProps> = ({ messages, isLoading }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto p-6 space-y-8 bg-black/40"
      style={{
        backgroundImage: 'linear-gradient(to bottom, rgba(0,0,0,0.5), rgba(0,0,0,0.8)), url("https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=2000&auto=format&fit=crop")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundBlendMode: 'multiply'
      }}
    >
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}
        >
          {msg.role === 'assistant' && (
            <div className="w-10 h-10 rounded-full border border-yellow-800 bg-[#2a241a] mr-3 mt-1 shadow-lg overflow-hidden">
              <img src={gojoImage} className="w-full h-full object-cover" alt="Satoru Gojo" />
            </div>
          )}

          <div className={`max-w-[80%] relative group`}>
            {msg.role === 'user' ? (
              <div className="bg-[#1a1a1a]/95 text-white p-4 rounded-xl border border-gray-700 shadow-xl flex items-center gap-4">
                <p className="flex-1">{msg.content}</p>
                <User size={24} className="opacity-40" />
              </div>
            ) : (
              <div className="bg-[#f0e6d2] text-[#2a241a] p-6 rounded-sm shadow-2xl border-[12px] border-double border-[#8b7355] relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none" style={{ backgroundImage: 'url("https://www.transparenttextures.com/patterns/parchment.png")' }}></div>
                <h4 className="cinzel-font font-bold mb-2 text-xs uppercase tracking-tighter border-b border-[#2a241a]/20 pb-1">Satoru Gojo</h4>
                <div className="medieval-font text-lg leading-relaxed">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({ node, ...props }) => <p className="mb-4 last:mb-0" {...props} />,
                      strong: ({ node, ...props }) => <strong className="font-bold text-[#4a3b2a]" {...props} />,
                      ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-4 space-y-1" {...props} />,
                      ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-4 space-y-1" {...props} />,
                      li: ({ node, ...props }) => <li className="marker:text-[#8b7355]" {...props} />,
                      h1: ({ node, ...props }) => <h1 className="cinzel-font text-2xl font-bold mb-3 mt-4 border-b border-[#8b7355]/30 pb-1" {...props} />,
                      h2: ({ node, ...props }) => <h2 className="cinzel-font text-xl font-bold mb-2 mt-3" {...props} />,
                      h3: ({ node, ...props }) => <h3 className="cinzel-font text-lg font-bold mb-2 mt-3" {...props} />,
                      code: ({ className, children, ...props }: any) => {
                        const match = /language-(\w+)/.exec(className || '')
                        const isInline = !match && !String(children).includes('\n')
                        return isInline ? (
                          <code className="bg-[#e6dac3] px-1.5 py-0.5 rounded font-mono text-sm border border-[#d4c5a5] text-[#5c4d3c]" {...props}>
                            {children}
                          </code>
                        ) : (
                          <code className="block bg-[#2a241a] text-[#f0e6d2] p-4 rounded-lg overflow-x-auto mb-4 border border-[#8b7355] text-sm font-mono" {...props}>
                            {children}
                          </code>
                        )
                      },
                      blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-[#8b7355] pl-4 italic my-4 bg-[#e6dac3]/30 py-2 pr-2 rounded-r" {...props} />,
                      a: ({ node, ...props }) => <a className="text-[#8b7355] font-bold underline hover:text-[#5c4d3c] transition-colors" target="_blank" rel="noopener noreferrer" {...props} />,
                      table: ({ node, ...props }) => <div className="overflow-x-auto mb-4"><table className="w-full text-left border-collapse border border-[#8b7355]/30" {...props} /></div>,
                      th: ({ node, ...props }) => <th className="bg-[#e6dac3] p-2 border border-[#8b7355]/30 font-bold cinzel-font" {...props} />,
                      td: ({ node, ...props }) => <td className="p-2 border border-[#8b7355]/30" {...props} />,
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
                <div className="mt-4 flex justify-between items-center opacity-40 text-[10px] font-bold uppercase cinzel-font">
                  <span>Monster Hunter World</span>
                  <span>Criado por Little Jão</span>
                </div>
              </div>
            )}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-[#f0e6d2] text-[#2a241a] p-4 rounded-sm border-4 border-double border-[#8b7355] animate-pulse">
            <p className="medieval-font">Pensando...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatArea;
