import React from 'react';

const LEVELS = [
  { id: 'L1', title: 'Level 1: Seedling', sub: 'Phonics & Words', emoji: '🌱' },
  { id: 'L2', title: 'Level 2: Explorer', sub: 'Phrases & Colors', emoji: '🚀' },
  { id: 'L3', title: 'Level 3: Storyteller', sub: 'Mini-Stories', emoji: '📖' },
];

export default function LevelSelector({ currentLevel = 'L1', onSelectLevel }) {
  return (
    <div className="flex items-center gap-1.5 overflow-x-auto py-1 px-1 scrollbar-none">
      <span className="text-xs font-black text-amber-900/70 uppercase tracking-wider whitespace-nowrap pl-1">
        Level:
      </span>
      <div className="flex items-center gap-1.5">
        {LEVELS.map((lvl) => {
          const isSelected = currentLevel === lvl.id;
          return (
            <button
              key={lvl.id}
              onClick={() => onSelectLevel(lvl.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold transition transform active:scale-95 shadow-sm whitespace-nowrap ${
                isSelected
                  ? 'bg-amber-400 text-amber-950 border-amber-500 shadow-md ring-2 ring-amber-300'
                  : 'bg-white/80 hover:bg-white text-slate-700 border-amber-200'
              }`}
            >
              <span>{lvl.emoji}</span>
              <span>{lvl.id}</span>
              <span className="hidden md:inline font-normal text-[11px] opacity-80">({lvl.sub})</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
