import React from 'react';
import { Star, Sparkles, Award } from 'lucide-react';

export default function Header({
  childName = 'Little Explorer',
  currentLevel = 'L1',
  stars = 0,
  levelUpRecommended = False,
  onLevelUp,
}) {
  const levelNames = {
    L1: '🌱 L1 Seedling (Ages 3-4)',
    L2: '🚀 L2 Explorer (Ages 4-5)',
    L3: '📖 L3 Storyteller (Ages 6-7)',
  };

  return (
    <header className="bg-white/90 backdrop-blur-md border-b-2 border-amber-200 shadow-sm sticky top-0 z-30 px-4 py-3">
      <div className="max-w-4xl mx-auto flex items-center justify-between gap-2">
        {/* Logo & Mascot */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-amber-400 rounded-2xl flex items-center justify-center shadow-md animate-bounce">
            <span className="text-2xl" role="img" aria-label="Robot">🤖</span>
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-black text-amber-900 tracking-tight flex items-center gap-1.5">
              Buddy <Sparkles className="w-5 h-5 text-amber-500 fill-amber-400 inline" />
            </h1>
            <p className="text-xs font-bold text-amber-700/80">
              English Learning Friend (Under 7)
            </p>
          </div>
        </div>

        {/* Stars and Level Badge */}
        <div className="flex items-center gap-2 md:gap-3">
          {/* Level Pill */}
          <div className="hidden sm:flex items-center px-3 py-1.5 bg-sky-100 border border-sky-300 rounded-xl text-sky-800 text-xs font-bold shadow-sm">
            {levelNames[currentLevel] || currentLevel}
          </div>

          {/* Star Counter with Pop Animation */}
          <div className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-amber-400 to-yellow-400 text-amber-950 font-black rounded-2xl shadow-md border-2 border-yellow-200">
            <Star className="w-5 h-5 fill-amber-900 text-amber-900 animate-spin" style={{ animationDuration: '6s' }} />
            <span className="text-lg md:text-xl font-extrabold">{stars}</span>
            <span className="text-xs uppercase tracking-wider font-bold hidden xs:inline">Stars</span>
          </div>
        </div>
      </div>

      {/* Level Up Banner Alert */}
      {levelUpRecommended && (
        <div className="max-w-4xl mx-auto mt-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl shadow-md flex items-center justify-between animate-pulse">
          <div className="flex items-center gap-2 text-sm font-bold">
            <Award className="w-5 h-5 text-yellow-300" />
            <span>🎉 Hooray! You've earned enough stars for the next adventure!</span>
          </div>
          {onLevelUp && (
            <button
              onClick={onLevelUp}
              className="px-3 py-1 bg-yellow-400 hover:bg-yellow-300 text-amber-950 font-black text-xs rounded-lg shadow transition transform active:scale-95"
            >
              Level Up 🚀
            </button>
          )}
        </div>
      )}
    </header>
  );
}
