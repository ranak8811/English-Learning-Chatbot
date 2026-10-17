import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import { Sparkles } from 'lucide-react';

const LEVEL_SUGGESTIONS = {
  L1: [
    { label: "Cat 🐱", text: "Cat" },
    { label: "Apple 🍎", text: "Apple" },
    { label: "Sun ☀️", text: "Sun" },
    { label: "I'm tired 😴", text: "I'm tired" },
  ],
  L2: [
    { label: "The dog runs! 🐶", text: "The dog runs!" },
    { label: "I like apples! 🍎", text: "I like apples!" },
    { label: "Two birds 🐦", text: "Two birds" },
    { label: "Tell a joke 🤪", text: "Tell me a silly joke!" },
  ],
  L3: [
    { label: "Tell a story! 📖", text: "Tell me a short story about a brave puppy!" },
    { label: "Why is sky blue? 🌤️", text: "Why is the sky blue, Buddy?" },
    { label: "Play a game! 🎮", text: "Let's play a fun word game!" },
  ],
};

export default function ChatWindow({
  messages = [],
  isLoading = false,
  currentLevel = 'L1',
  onSelectSuggestion,
  onSpeak,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const suggestions = LEVEL_SUGGESTIONS[currentLevel] || LEVEL_SUGGESTIONS.L1;

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2">
      {/* Welcome Banner if few messages */}
      {messages.length <= 1 && (
        <div className="max-w-md mx-auto text-center my-6 p-6 bg-amber-100/70 border-2 border-dashed border-amber-300 rounded-3xl shadow-sm">
          <div className="w-16 h-16 mx-auto mb-3 bg-amber-300 rounded-full flex items-center justify-center text-3xl shadow-inner animate-float">
            👋
          </div>
          <h2 className="text-xl font-black text-amber-950 mb-1">
            Welcome to English Buddy!
          </h2>
          <p className="text-sm font-medium text-amber-900/80 mb-4">
            Tap a quick word below or use the microphone to talk with Buddy!
          </p>
        </div>
      )}

      {/* Message List */}
      {messages.map((msg, index) => (
        <MessageBubble key={index} message={msg} onSpeak={onSpeak} />
      ))}

      {/* Loading / Typing Indicator */}
      {isLoading && (
        <div className="flex items-center gap-2 text-slate-500 p-3 bg-sky-50 rounded-2xl border border-sky-100 max-w-[200px] shadow-sm animate-pulse">
          <span className="text-xl animate-spin" style={{ animationDuration: '3s' }}>🎈</span>
          <span className="text-xs font-bold text-sky-800">Buddy is thinking...</span>
        </div>
      )}

      {/* Quick Suggestion Chips */}
      {!isLoading && (
        <div className="pt-2">
          <div className="flex items-center gap-1.5 mb-1.5 px-1">
            <Sparkles className="w-3.5 h-3.5 text-amber-600" />
            <span className="text-[11px] font-black uppercase tracking-wider text-amber-800/70">
              Quick Words:
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {suggestions.map((s, idx) => (
              <button
                key={idx}
                onClick={() => onSelectSuggestion && onSelectSuggestion(s.text)}
                className="px-3 py-1.5 bg-white hover:bg-amber-100 text-slate-800 border border-amber-300 rounded-xl text-xs font-bold shadow-2xs transition transform active:scale-95"
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
