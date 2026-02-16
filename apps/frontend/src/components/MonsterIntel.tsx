
import React from 'react';
import { Reward } from '../types';

interface MonsterIntelProps {
  name: string;
  weakness: string[];
  resistances: string[];
  breakableParts: string[];
  rewards?: Record<string, Reward[]>;
  image: string;
}

const MonsterIntel: React.FC<MonsterIntelProps> = ({
  name,
  weakness,
  resistances,
  breakableParts,
  rewards = {},
  image
}) => {
  const [imgSrc, setImgSrc] = React.useState(image);

  React.useEffect(() => {
    setImgSrc(image);
  }, [image]);

  return (
    <aside className="w-72 bg-[#141414]/90 backdrop-blur-sm border-l border-[#2a2a2a] p-4 flex flex-col gap-6 overflow-y-auto">
      <div className="space-y-4">
        <h2 className="text-lg cinzel-font font-bold text-center py-2 border-b border-[#333]">Monster Intel: {name}</h2>

        <div className="relative group overflow-hidden rounded-lg border-2 border-[#333] shadow-inner bg-black">
          <img
            src={imgSrc}
            alt={name}
            className="w-full h-40 object-cover opacity-80 group-hover:opacity-100 transition-opacity"
            onError={() => setImgSrc(`https://picsum.photos/seed/${name}/800/600`)}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        </div>
      </div>

      <div className="space-y-6 text-sm">
        <section>
          <h3 className="text-gray-200 font-bold uppercase tracking-widest text-xs mb-2 flex items-center gap-2">
            <span className="w-1 h-4 bg-red-700"></span> Weakness
          </h3>
          <ul className="text-gray-400 space-y-1 list-disc list-inside">
            {weakness.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </section>

        <section>
          <h3 className="text-gray-200 font-bold uppercase tracking-widest text-xs mb-2 flex items-center gap-2">
            <span className="w-1 h-4 bg-blue-700"></span> Resistances
          </h3>
          <ul className="text-gray-400 space-y-1 list-disc list-inside">
            {resistances.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </section>

        <section>
          <h3 className="text-gray-200 font-bold uppercase tracking-widest text-xs mb-2 flex items-center gap-2">
            <span className="w-1 h-4 bg-green-700"></span> Breakable Parts
          </h3>
          <p className="text-gray-400 leading-relaxed italic">
            {breakableParts.join(', ')}
          </p>
        </section>

        {Object.keys(rewards).length > 0 && (
          <section>
            <h3 className="text-gray-200 font-bold uppercase tracking-widest text-xs mb-2 flex items-center gap-2">
              <span className="w-1 h-4 bg-yellow-600"></span> Key Drops
            </h3>
            <div className="space-y-4 mt-3">
              {(Object.entries(rewards) as [string, Reward[]][]).map(([rank, items]) => (
                <div key={rank} className="space-y-1">
                  <h4 className="text-xs font-semibold text-yellow-500/80 uppercase tracking-wider pl-2">{rank}</h4>
                  <ul className="text-gray-400 space-y-1 text-xs pl-2 border-l border-zinc-800 ml-1">
                    {items.slice(0, 4).map((r, i) => (
                      <li key={i} className="flex justify-between items-center group cursor-default py-0.5">
                        <span className="group-hover:text-yellow-100 transition-colors truncate pr-2" title={r.item}>{r.item}</span>
                        <span className="text-zinc-600 text-[10px] font-mono whitespace-nowrap min-w-[30px] text-right">{r.chance}%</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </aside>
  );
};

export default MonsterIntel;
