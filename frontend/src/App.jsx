import React, { useState, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';
import Header from './components/Header';
import LevelSelector from './components/LevelSelector';
import MoodSelector from './components/MoodSelector';
import ChatWindow from './components/ChatWindow';
import VoiceInput from './components/VoiceInput';
import { sendChatMessage, getOrCreateChildProfile, recordChildMood } from './services/api';
import { speakText, stopSpeech } from './services/speech';

const INITIAL_MESSAGES = [
  {
    role: 'assistant',
    content: "Hello little explorer! 🌟 I'm Buddy! Let's play and learn English together! Can you say: 'Cat'? 🐱",
    detected_mode: 'learning',
    detected_emotion: 'happy',
    latency_ms: 120,
    stars_awarded: 0,
  },
];

export default function App() {
  const [childId, setChildId] = useState(null);
  const [childName, setChildName] = useState('Leo');
  const [currentLevel, setCurrentLevel] = useState('L1');
  const [selectedMood, setSelectedMood] = useState('happy');
  const [stars, setStars] = useState(0);
  const [levelUpRecommended, setLevelUpRecommended] = useState(false);
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);

  // Initialize or load child profile on component mount
  useEffect(() => {
    async function initProfile() {
      try {
        const profile = await getOrCreateChildProfile('Leo', 5, 'L1');
        setChildId(profile.id);
        setChildName(profile.name);
        setCurrentLevel(profile.current_level);
        setStars(profile.stars_earned || 0);
      } catch (err) {
        console.warn('Backend offline or initializing; using local session state:', err);
      }
    }
    initProfile();
  }, []);

  const handleToggleSound = () => {
    setSoundEnabled((prev) => {
      const next = !prev;
      if (!next) {
        stopSpeech();
      }
      return next;
    });
  };

  const handleVoiceTranscript = (text, isFinal) => {
    setInputText(text);
  };

  const handleSpeak = (text) => {
    if (soundEnabled && text) {
      speakText(text);
    }
  };

  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputText).trim();
    if (!text || isLoading) return;

    // Stop ongoing speech before sending new message
    stopSpeech();

    // 1. Immediately render child's utterance
    const userTurn = {
      role: 'user',
      content: text,
    };
    setMessages((prev) => [...prev, userTurn]);
    setInputText('');
    setIsLoading(true);

    try {
      // 2. Dispatch to FastAPI backend (<2s SLA)
      const data = await sendChatMessage({
        message: text,
        childId,
        level: currentLevel,
        mood: selectedMood,
      });

      // 3. Render Buddy's response
      const assistantTurn = {
        role: 'assistant',
        content: data.reply,
        detected_mode: data.detected_mode,
        detected_emotion: data.detected_emotion,
        latency_ms: data.latency_ms,
        stars_awarded: data.stars_awarded || 0,
      };

      setMessages((prev) => [...prev, assistantTurn]);

      // 4. Automatically narrate response aloud with child-friendly pitch
      if (soundEnabled && data.reply) {
        speakText(data.reply);
      }

      // 5. Update rewards and levels
      if (typeof data.total_stars === 'number') {
        setStars(data.total_stars);
      }
      if (data.level && data.level !== currentLevel) {
        setCurrentLevel(data.level);
      }
      if (data.level_up_recommended) {
        setLevelUpRecommended(true);
      }
    } catch (err) {
      console.error('Chat error:', err);
      // Fallback friendly message if network dropped
      const fallbackReply = "You did a super try! 🌟 Let's keep exploring! Can you say: 'Dog'? 🐶";
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: fallbackReply,
          detected_mode: 'learning',
          detected_emotion: 'happy',
          latency_ms: 50,
          stars_awarded: 0,
        },
      ]);
      if (soundEnabled) {
        speakText(fallbackReply);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectMood = async (newMood) => {
    setSelectedMood(newMood);
    if (childId) {
      try {
        await recordChildMood(childId, newMood);
      } catch (e) {
        console.debug('Mood log deferred:', e);
      }
    }
  };

  const handleSelectLevel = (newLevel) => {
    setCurrentLevel(newLevel);
    setLevelUpRecommended(false);
  };

  const handleLevelUp = () => {
    if (currentLevel === 'L1') setCurrentLevel('L2');
    else if (currentLevel === 'L2') setCurrentLevel('L3');
    setLevelUpRecommended(false);
  };

  return (
    <div className="flex flex-col h-screen max-h-screen bg-gradient-to-b from-amber-50 via-yellow-50 to-orange-50 font-sans text-slate-800">
      {/* 1. Top Header */}
      <Header
        childName={childName}
        currentLevel={currentLevel}
        stars={stars}
        levelUpRecommended={levelUpRecommended}
        soundEnabled={soundEnabled}
        onToggleSound={handleToggleSound}
        onLevelUp={handleLevelUp}
      />

      {/* 2. Interactive Controls (Level Switcher & Emotion Selector) */}
      <div className="bg-white/80 border-b border-amber-200 px-4 py-2 shadow-2xs">
        <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <LevelSelector currentLevel={currentLevel} onSelectLevel={handleSelectLevel} />
          <MoodSelector selectedMood={selectedMood} onSelectMood={handleSelectMood} />
        </div>
      </div>

      {/* 3. Main Chat Viewport */}
      <main className="flex-1 overflow-hidden flex flex-col max-w-4xl w-full mx-auto">
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          currentLevel={currentLevel}
          onSelectSuggestion={handleSendMessage}
          onSpeak={handleSpeak}
        />

        {/* 4. Bottom Input Bar with Voice Microphone and Quick Send */}
        <div className="p-3 md:p-4 bg-white/95 border-t-2 border-amber-200 shadow-lg">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center gap-2 max-w-3xl mx-auto"
          >
            {/* Multimodal Speech-to-Text Microphone Input */}
            <VoiceInput
              onTranscript={handleVoiceTranscript}
              disabled={isLoading}
            />

            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Say or type something to Buddy... 🎈"
              disabled={isLoading}
              className="flex-1 px-4 py-3.5 bg-amber-50/70 focus:bg-white border-2 border-amber-300 focus:border-amber-500 rounded-2xl text-base md:text-lg text-slate-800 placeholder-slate-400 outline-none transition shadow-inner font-medium"
            />

            <button
              type="submit"
              disabled={isLoading || !inputText.trim()}
              className="px-5 py-3.5 bg-amber-400 hover:bg-amber-300 disabled:bg-slate-200 disabled:text-slate-400 text-amber-950 font-black rounded-2xl shadow-md border-2 border-amber-500 transition transform active:scale-95 flex items-center gap-1.5 flex-shrink-0"
              title="Send message"
            >
              <Send className="w-5 h-5 text-amber-950" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
