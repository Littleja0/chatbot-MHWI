
import React, { useState } from 'react';
import { Sword } from 'lucide-react';

interface InputBarProps {
  onSendMessage: (msg: string) => void;
  disabled: boolean;
}

const InputBar: React.FC<InputBarProps> = ({ onSendMessage, disabled }) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="h-24 bg-[#111] border-t border-[#2a2a2a] flex items-center px-6 gap-6 shadow-[0_-10px_30px_rgba(0,0,0,0.5)]">


      <div className="flex-1 relative flex items-center">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          disabled={disabled}
          placeholder="Digite sua pergunta para o Sensei..."
          className="w-full bg-[#1a1a1a] border-2 border-[#333] rounded-lg px-4 py-3 pr-16 text-gray-200 focus:outline-none focus:border-[#5a5a5a] resize-none h-14 leading-tight transition-all disabled:opacity-50 shadow-inner"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-[#333] hover:bg-[#444] disabled:opacity-30 rounded-lg flex items-center justify-center transition-all group border border-[#444]"
        >
          <Sword size={20} className="text-gray-400 group-hover:text-white group-hover:rotate-12 transition-transform" />
        </button>
      </div>
    </div>
  );
};

export default InputBar;
