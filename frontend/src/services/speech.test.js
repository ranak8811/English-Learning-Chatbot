import test, { describe, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import {
  isSpeechSynthesisSupported,
  isSpeechRecognitionSupported,
  cleanTextForSpeech,
  speakText,
  stopSpeech,
  createSpeechRecognizer,
} from './speech.js';

describe('Web Speech Service', () => {
  beforeEach(() => {
    // Reset global window mocks before each test
    delete global.window;
  });

  test('EC-08: Gracefully returns false in non-browser environment without errors', () => {
    assert.equal(isSpeechSynthesisSupported(), false);
    assert.equal(isSpeechRecognitionSupported(), false);
    assert.equal(speakText('Hello!'), null);
    assert.equal(createSpeechRecognizer(), null);
  });

  test('cleanTextForSpeech removes markdown formatting and emojis', () => {
    const raw = '**Great job!** 🌟 You found the 🍎 red apple! *Hooray!*';
    const cleaned = cleanTextForSpeech(raw);
    assert.equal(cleaned, 'Great job! You found the red apple! Hooray!');
  });

  test('cleanTextForSpeech handles null and undefined gracefully', () => {
    assert.equal(cleanTextForSpeech(null), '');
    assert.equal(cleanTextForSpeech(undefined), '');
    assert.equal(cleanTextForSpeech(123), '');
  });

  test('FR-CTX-02 / Scenario 1: Speech synthesis instantiates with rate: 0.95 and pitch: 1.1', () => {
    let spokenUtterance = null;
    let cancelCalled = false;

    class MockSpeechSynthesisUtterance {
      constructor(text) {
        this.text = text;
        this.rate = 1.0;
        this.pitch = 1.0;
        this.volume = 1.0;
        this.lang = '';
      }
    }

    const mockSpeechSynthesis = {
      speak: (utt) => {
        spokenUtterance = utt;
      },
      cancel: () => {
        cancelCalled = true;
      },
      getVoices: () => [
        { name: 'Google US English', lang: 'en-US' },
        { name: 'Victoria', lang: 'en-GB' },
      ],
    };

    global.window = {
      speechSynthesis: mockSpeechSynthesis,
      SpeechSynthesisUtterance: MockSpeechSynthesisUtterance,
    };

    assert.equal(isSpeechSynthesisSupported(), true);

    const utterance = speakText('Hello child! 🦁');
    assert.ok(utterance, 'Utterance should be returned');
    assert.equal(cancelCalled, true, 'Should cancel previous speech');
    assert.equal(utterance.text, 'Hello child!');
    assert.equal(utterance.rate, 0.95);
    assert.equal(utterance.pitch, 1.1);
    assert.equal(utterance.voice.name, 'Google US English');
  });

  test('FR-CTX-02 / Scenario 2: createSpeechRecognizer initializes webkitSpeechRecognition properly', () => {
    let startCalled = false;
    let stopCalled = false;

    class MockSpeechRecognition {
      constructor() {
        this.continuous = true;
        this.interimResults = false;
        this.lang = '';
        this.maxAlternatives = 0;
      }
      start() {
        startCalled = true;
        if (this.onstart) this.onstart();
      }
      stop() {
        stopCalled = true;
        if (this.onend) this.onend();
      }
      abort() {}
    }

    global.window = {
      webkitSpeechRecognition: MockSpeechRecognition,
    };

    assert.equal(isSpeechRecognitionSupported(), true);

    let started = false;
    let ended = false;
    let resultPayload = null;

    const recognizer = createSpeechRecognizer({
      onStart: () => {
        started = true;
      },
      onEnd: () => {
        ended = true;
      },
      onResult: (res) => {
        resultPayload = res;
      },
    });

    assert.ok(recognizer);
    recognizer.start();
    assert.equal(startCalled, true);
    assert.equal(started, true);

    // Simulate interim result event
    recognizer.raw.onresult({
      resultIndex: 0,
      results: [
        Object.assign([{ transcript: 'yellow banana' }], { isFinal: false }),
      ],
    });
    assert.ok(resultPayload);
    assert.equal(resultPayload.text, 'yellow banana');
    assert.equal(resultPayload.isFinal, false);

    // Simulate final result event
    recognizer.raw.onresult({
      resultIndex: 0,
      results: [
        Object.assign([{ transcript: 'yellow banana' }], { isFinal: true }),
      ],
    });
    assert.equal(resultPayload.text, 'yellow banana');
    assert.equal(resultPayload.isFinal, true);

    recognizer.stop();
    assert.equal(stopCalled, true);
    assert.equal(ended, true);
  });
});
