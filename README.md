# AI-Powered English Learning Chatbot for Children (Under 7)

An interactive, emotionally intelligent, and adaptive English learning companion built specifically for early childhood education (ages 3–7).

Built for **BRIMSEL Evaluation (Full-Stack AI Engineer)**.

---

## 🌟 Core Highlights & Architectural Features

1. **Progressive Learning Engine (L1, L2, L3):**
   * **Level 1 (Seedling - Ages 3–4):** Alphabet phonics, single vocabulary words, animal sounds.
   * **Level 2 (Explorer - Ages 4–5):** 2–3 word phrases, counting, colors, opposites, simple sentences.
   * **Level 3 (Storyteller - Ages 6–7):** Interactive dialogues, "why" questions, mini-story choices.
   * **Adaptive Star Progression:** Dynamically scales challenge based on child mastery and engagement.
2. **Child Mode Detection:**
   * Dynamically switches between **Learning**, **Conversation** (friendly chat), **Engagement** (rhymes/animal sounds/games when attention wanes), and **Support** (comforting reassurance when frustrated or tired).
3. **Social & Emotional Learning (SEL):**
   * Growth mindset positive reinforcement (zero harsh error corrections; mistakes are celebrated as learning steps).
   * Visual emotion selector (Happy, Curious, Silly, Sleepy) and star reward animations.
4. **Multimodal Voice Interaction:**
   * Browser-native Web Speech API (`webkitSpeechRecognition` for microphone input and `SpeechSynthesis` for audio readouts).
5. **Strict <2-Second Latency SLA:**
   * Ultra-fast inference with OpenRouter `google/gemma-4-26b-a4b-it:free` (with token clamping and prompt optimization).
   * Asynchronous database writes using FastAPI background tasks.
6. **Robust Data Persistence:**
   * Cloud PostgreSQL hosted on **Neon Serverless** with SSL connection pooling.

---

## 🛠️ Tech Stack

* **Frontend:** React 18, Vite, Tailwind CSS, Lucide React, Web Speech API (Deployed to Netlify / Vercel).
* **Backend:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, Pydantic v2 (Deployed to Render / Koyeb).
* **Database:** Neon Cloud Serverless PostgreSQL (`ep-gentle-cake-azij2y8q-pooler.c-3.ap-southeast-1.aws.neon.tech`).
* **LLM Engine:** OpenRouter (`google/gemma-4-26b-a4b-it:free` with fallback).

---

## 🚀 Local Development Setup

### 1. Prerequisites
* Python 3.10+
* Node.js 18+ & npm

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Running Automated Tests
```bash
cd backend
pytest -v tests/
```

---

## 👥 GitHub Collaborators
Invited BRIMSEL evaluators:
* `farzana@sharif.com`
* `masrur@sharif.com`
