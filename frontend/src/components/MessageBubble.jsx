import React from 'react';
import { Volume2, Star, Zap } from 'lucide-react';

export default function MessageBubble({ message, onSpeak }) {
  const isAssistant = message.role === 'assistant';

  const modeBadges = {
    learning: { label: 'Learning 🎓', bg: 'bg-emerald-100 text-emerald-800 border-emerald-200' },
    support: { label: 'Comfort & Support 💛', bg: 'bg-amber-100 text-amber-900 border-amber-300' },
    engagement: { label: 'Play & Fun 🎈', bg: 'bg-purple-100 text-purple-900 border-purple-200' },
    conversation: { label: 'Buddy Chat 💬', bg: 'bg-blue-100 text-blue-900 border-blue-200' },
  };

  const badge = modeBadges[message.detected_mode] || modeBadges.learning;

  return (
    <div className={`flex items-end gap-2.5 mb-4 ${isAssistant ? 'justify-start' : 'justify-end'}`}>
      {/* Buddy Mascot Avatar */}
      {isAssistant && (
        <div className="w-10 h-10 md:w-12 md:h-12 rounded-2xl bg-sky-200 border-2 border-sky-300 flex items-center justify-center shadow-sm flex-shrink-0 animate-float">
          <span className="text-xl md:text-2xl" role="img" aria-label="Buddy">🤖</span>
        </div>
      )}

      {/* Bubble Container */}
      <div className={`max-w-[85%] sm:max-w-[75%] md:max-w-[70%] flex flex-col ${isAssistant ? 'items-start' : 'items-end'}`}>
        {/* Assistant Header Badges */}
        {isAssistant && (
          <div className="flex items-center gap-1.5 mb-1 px-1">
            <span className="text-xs font-black text-slate-600">Buddy</span>
            {message.detected_mode && (
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border shadow-2xs ${badge.bg}`}>
                {badge.label}
              </span>
            )}
            {message.latency_ms && (
              <span className="text-[10px] font-bold px-1.5 py-0.5 bg-slate-100 text-slate-500 rounded-md border border-slate-200 flex items-center gap-0.5">
                <Zap className="w-2.5 h-2.5 text-amber-500 fill-amber-400" />
                {message.latency_ms}ms
              </span>
            )}
          </div>
        )}

        {/* Message Bubble Body */}
        <div
          className={`p-4 md:p-5 rounded-3xl shadow-md border-2 leading-relaxed text-base md:text-lg font-medium transition ${
            isAssistant
              ? 'bg-sky-50 border-sky-200 text-slate-900 rounded-bl-sm'
              : 'bg-amber-400 border-amber-500 text-amber-950 font-semibold rounded-br-sm shadow-amber-200/50'
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>

          {/* Action Bar inside Assistant Bubble */}
          {isAssistant && (
            <div className="mt-3 pt-2.5 border-t border-sky-200/60 flex items-center justify-between gap-3">
              {/* Speaker Audio Playback Button */}
              <button
                onClick={() => onSpeak && onSpeak(message.content)}
                className="flex items-center gap-1.5 px-3 py-1 bg-white hover:bg-sky-100 text-sky-800 rounded-xl text-xs font-bold border border-sky-200 shadow-xs transition active:scale-95"
                title="Listen to Buddy speak"
              >
                <Volume2 className="w-4 h-4 text-sky-600" />
                <span>Listen</span>
              </button>

              {/* Star Notification Tag */}
              {message.stars_awarded > 0 && (
                <div className="flex items-center gap-1 px-2.5 py-1 bg-yellow-300 text-amber-950 rounded-xl text-xs font-black border border-yellow-400 shadow-xs animate-bounce">
                  <Star className="w-3.5 h-3.5 fill-amber-900 text-amber-900" />
                  <span>+1 Star!</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Child Avatar */}
      {!isAssistant && (
        <div className="w-10 h-10 md:w-12 md:h-12 rounded-2xl bg-amber-200 border-2 border-amber-300 flex items-center justify-center shadow-sm flex-shrink-0">
          <span className="text-xl md:text-2xl" role="img" aria-label="Child">🧒</span>
        </div>
      )}
    </div>
  );
}
