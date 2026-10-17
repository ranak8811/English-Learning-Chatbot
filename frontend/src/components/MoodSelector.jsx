import React from 'react';
import { Smile, HelpCircle, Sparkles, Moon } from 'lucide-react';

const MOODS = [
  { id: 'happy', label: 'Happy', emoji: '😊', bg: 'bg-emerald-100 hover:bg-emerald-200 border-emerald-300 text-emerald-900', active: 'ring-2 ring-emerald-500 bg-emerald-200' },
  { id: 'curious', label: 'Curious', emoji: '🧐', bg: 'bg-indigo-100 hover:bg-indigo-200 border-indigo-300 text-indigo-900', active: 'ring-2 ring-indigo-500 bg-indigo-200' },
  { id: 'silly', label: 'Silly', emoji: '🤪', bg: 'bg-fuchsia-100 hover:bg-fuchsia-200 border-fuchsia-300 text-fuchsia-900', active: 'ring-2 ring-fuchsia-500 bg-fuchsia-200' },
  { id: 'sleepy', label: 'Sleepy', emoji: '😴', bg: 'bg-purple-100 hover:bg-purple-200 border-purple-300 text-purple-900', active: 'ring-2 ring-purple-500 bg-purple-200' },
];

export default function MoodSelector({ selectedMood = 'happy', onSelectMood }) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto py-1 px-1 scrollbar-none">
      <span className="text-xs font-black text-amber-900/70 uppercase tracking-wider whitespace-nowrap pl-1">
        Feeling:
      </span>
      <div className="flex items-center gap-1.5">
        {MOODS.map((m) => {
          const isSelected = selectedMood === m.id;
          return (
            <button
              key={m.id}
              onClick={() => onSelectMood(m.id)}
              className={`flex items-center gap-1 px-2.5 py-1.5 rounded-xl border text-xs font-bold transition transform active:scale-95 shadow-sm ${m.bg} ${
                isSelected ? m.active : 'opacity-85'
              }`}
              title={`I feel ${m.label}`}
            >
              <span className="text-sm">{m.emoji}</span>
              <span className="hidden sm:inline">{m.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
