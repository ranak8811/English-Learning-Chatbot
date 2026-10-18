import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { isSpeechRecognitionSupported, createSpeechRecognizer } from '../services/speech';

export default function VoiceInput({ onTranscript, disabled = false }) {
  const [isListening, setIsListening] = useState(false);
  const [supported, setSupported] = useState(true);
  const [statusMessage, setStatusMessage] = useState('');
  const recognizerRef = useRef(null);

  useEffect(() => {
    setSupported(isSpeechRecognitionSupported());
  }, []);

  const handleToggleListening = () => {
    if (disabled) return;

    if (isListening) {
      if (recognizerRef.current) {
        recognizerRef.current.stop();
      }
      setIsListening(false);
      setStatusMessage('');
      return;
    }

    const recognizer = createSpeechRecognizer({
      onStart: () => {
        setIsListening(true);
        setStatusMessage('Listening to your lovely voice... 🎙️');
      },
      onResult: ({ text, isFinal }) => {
        if (text) {
          onTranscript(text, isFinal);
          if (isFinal) {
            setStatusMessage(`Heard: "${text}" ✨`);
          }
        }
      },
      onError: (err) => {
        console.warn('Speech recognition error:', err);
        setIsListening(false);
        if (err.error === 'not-allowed') {
          setStatusMessage('Microphone permission blocked. Please allow mic access! 🔒');
        } else {
          setStatusMessage('Could not hear clearly. Tap to try again! 🎈');
        }
        setTimeout(() => setStatusMessage(''), 4000);
      },
      onEnd: () => {
        setIsListening(false);
        setTimeout(() => setStatusMessage(''), 2000);
      },
    });

    if (recognizer) {
      recognizerRef.current = recognizer;
      recognizer.start();
    }
  };

  // Unsupported browser fallback
  if (!supported) {
    return (
      <div
        className="flex items-center gap-1 px-3 py-2 bg-slate-100 border border-slate-300 rounded-2xl text-slate-400 text-xs font-semibold cursor-not-allowed select-none"
        title="Speech recognition is not supported in this browser. You can type messages directly!"
      >
        <MicOff className="w-5 h-5 text-slate-400" />
        <span className="hidden sm:inline">Voice off</span>
      </div>
    );
  }

  return (
    <div className="relative flex items-center">
      {/* Floating Status Notification for Child */}
      {statusMessage && (
        <div className="absolute -top-10 left-1/2 -translate-x-1/2 whitespace-nowrap px-3 py-1 bg-amber-900 text-amber-100 rounded-xl text-xs font-bold shadow-lg animate-bounce z-40 border border-amber-700">
          {statusMessage}
        </div>
      )}

      {/* Child-Friendly Pulse Button */}
      <button
        type="button"
        onClick={handleToggleListening}
        disabled={disabled}
        className={`relative p-3.5 rounded-2xl font-black transition-all transform active:scale-95 flex items-center justify-center shadow-md flex-shrink-0 ${
          isListening
            ? 'bg-rose-500 hover:bg-rose-600 text-white border-2 border-rose-600 animate-pulse'
            : 'bg-amber-100 hover:bg-amber-200 text-amber-900 border-2 border-amber-300'
        }`}
        title={isListening ? 'Listening... Tap to stop' : 'Tap to speak with Buddy! 🎤'}
        aria-label={isListening ? 'Stop listening' : 'Start voice recording'}
      >
        {isListening && (
          <span className="absolute -inset-1 rounded-2xl bg-rose-400 animate-ping opacity-75" />
        )}
        <Mic className={`w-6 h-6 relative z-10 ${isListening ? 'text-white' : 'text-amber-800'}`} />
      </button>
    </div>
  );
}
