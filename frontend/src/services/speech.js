/**
 * Web Speech API Service
 * Handles Speech-to-Text (STT) and child-friendly Text-to-Speech (TTS).
 * Rate: 0.95, Pitch: 1.1 for warm, encouraging early-childhood tone.
 */

/**
 * Checks whether Speech Synthesis (TTS) is supported in the current browser.
 */
export function isSpeechSynthesisSupported() {
  return typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
}

/**
 * Checks whether Speech Recognition (STT) is supported in the current browser.
 */
export function isSpeechRecognitionSupported() {
  if (typeof window === 'undefined') return false;
  return Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
}

/**
 * Cleans text before TTS to remove markdown, excessive punctuation, and emojis
 * so synthesized speech sounds natural and clear for a young child.
 */
export function cleanTextForSpeech(text) {
  if (!text || typeof text !== 'string') return '';
  return text
    // Remove markdown formatting like **bold** or *italic*
    .replace(/\*+/g, '')
    // Remove code blocks and backticks
    .replace(/`+/g, '')
    // Remove emoji symbols across all Unicode pictographic ranges
    .replace(/\p{Extended_Pictographic}/gu, '')
    // Replace multiple spaces with single space
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Speaks text using the browser SpeechSynthesis API.
 * Uses rate 0.95 and pitch 1.1 to deliver a warm, gentle early-childhood tone.
 *
 * @param {string} text - Message to read aloud.
 * @param {Object} options - Configuration overrides.
 * @returns {SpeechSynthesisUtterance|null}
 */
export function speakText(text, options = {}) {
  if (!isSpeechSynthesisSupported()) {
    console.warn('SpeechSynthesis is not supported in this browser.');
    return null;
  }

  const {
    rate = 0.95,
    pitch = 1.1,
    volume = 1.0,
    lang = 'en-US',
    onStart = null,
    onEnd = null,
    onError = null,
  } = options;

  // Cancel any currently playing speech first
  stopSpeech();

  const clean = cleanTextForSpeech(text);
  if (!clean) return null;

  const utterance = new window.SpeechSynthesisUtterance(clean);
  utterance.rate = rate;
  utterance.pitch = pitch;
  utterance.volume = volume;
  utterance.lang = lang;

  // Attempt to select a friendly English voice (Samantha, Victoria, Google US English, etc.)
  const voices = window.speechSynthesis.getVoices();
  if (voices && voices.length > 0) {
    const preferredVoice = voices.find(
      (v) =>
        (v.name.includes('Samantha') ||
          v.name.includes('Victoria') ||
          v.name.includes('Google US English') ||
          v.name.includes('Natural') ||
          v.name.includes('Zira')) &&
        v.lang.startsWith('en')
    ) || voices.find((v) => v.lang.startsWith('en'));

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }
  }

  if (onStart) utterance.onstart = onStart;
  if (onEnd) utterance.onend = onEnd;
  if (onError) utterance.onerror = onError;

  window.speechSynthesis.speak(utterance);
  return utterance;
}

/**
 * Cancels any ongoing speech synthesis.
 */
export function stopSpeech() {
  if (isSpeechSynthesisSupported()) {
    window.speechSynthesis.cancel();
  }
}

/**
 * Creates a Speech Recognition instance for converting voice input to text.
 *
 * @param {Object} callbacks
 * @param {Function} callbacks.onResult - Receives (finalTranscript, isFinal)
 * @param {Function} callbacks.onStart - Triggered when microphone starts listening
 * @param {Function} callbacks.onEnd - Triggered when microphone stops
 * @param {Function} callbacks.onError - Receives (errorEvent)
 * @param {string} callbacks.lang - BCP-47 language tag (default 'en-US')
 * @returns {Object|null} Controller object with start(), stop(), abort() methods
 */
export function createSpeechRecognizer({
  onResult,
  onStart,
  onEnd,
  onError,
  lang = 'en-US',
} = {}) {
  if (!isSpeechRecognitionSupported()) {
    console.warn('SpeechRecognition is not supported in this browser.');
    return null;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = lang;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    if (onStart) onStart();
  };

  recognition.onresult = (event) => {
    let interimTranscript = '';
    let finalTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcript;
      } else {
        interimTranscript += transcript;
      }
    }

    if (onResult) {
      onResult({
        final: finalTranscript.trim(),
        interim: interimTranscript.trim(),
        text: (finalTranscript || interimTranscript).trim(),
        isFinal: Boolean(finalTranscript),
      });
    }
  };

  recognition.onerror = (event) => {
    console.warn('Speech recognition error:', event.error);
    if (onError) onError(event);
  };

  recognition.onend = () => {
    if (onEnd) onEnd();
  };

  return {
    start: () => {
      try {
        recognition.start();
      } catch (err) {
        console.warn('Recognition start error:', err);
      }
    },
    stop: () => {
      try {
        recognition.stop();
      } catch (err) {
        console.warn('Recognition stop error:', err);
      }
    },
    abort: () => {
      try {
        recognition.abort();
      } catch (err) {
        console.warn('Recognition abort error:', err);
      }
    },
    raw: recognition,
  };
}
