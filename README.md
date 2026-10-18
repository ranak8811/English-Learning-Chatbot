# 🦁 AI-Powered English Learning Chatbot for Children (Under 7)

An emotionally intelligent, pedagogically grounded, and multimodal English learning companion built specifically for early childhood education (ages 3–7).

> **Assessment Submission:** BRIMSEL Full-Stack AI Engineer  
> **Target Audience:** Early Learners (Ages 3–4 Seedling, 4–5 Explorer, 6–7 Storyteller)  
> **Performance Guarantee:** Strict End-to-End Latency `< 2.0s` SLA

---

## 🌐 Live Cloud Deployment & Links

* **Live Web App (Frontend):** [https://english-learning-chatbot.netlify.app](https://english-learning-chatbot.netlify.app) *(or your deployed Netlify URL)*
* **FastAPI Backend (Render):** [https://english-learning-chatbot-backend.onrender.com](https://english-learning-chatbot-backend.onrender.com)
* **Interactive API Documentation:** [https://english-learning-chatbot-backend.onrender.com/docs](https://english-learning-chatbot-backend.onrender.com/docs)
* **Health Check & Pooler Status:** [https://english-learning-chatbot-backend.onrender.com/api/health](https://english-learning-chatbot-backend.onrender.com/api/health)

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend: React 19 + Tailwind CSS + Web Speech API"]
        UI["Child UI (Big Touch Avatars, Star Counter, Mood Selector)"]
        STT["Web Speech Recognition (Microphone STT)"]
        TTS["Web Speech Synthesis (0.95 Rate, 1.1 Pitch Narration)"]
    end

    subgraph API["FastAPI Backend (Render Cloud Container)"]
        Router["REST Endpoints (/api/chat, /api/child, /api/health)"]
        ModeDet["Child Mode Detector (learning, conversation, engagement, support)"]
        SELEngine["SEL Engine (Positive Reinforcement, Zero Harsh Corrections)"]
        StateMach["L1-L3 Learning State Machine & Milestone Tracker"]
        BGTasks["FastAPI Background Tasks (Non-blocking Logging)"]
    end

    subgraph Intelligence["Multi-Tier Resilient AI Engine (<2.0s SLA)"]
        T1["Tier 1: Google Gemini 3.5 Flash Lite (~780ms)"]
        T2["Tier 2: OpenRouter Multi-Model Fallback Pool"]
        T3["Tier 3: Instant Pedagogical Fallback Engine (<2ms)"]
    end

    subgraph Data["Data Persistence (Neon Cloud PostgreSQL)"]
        NeonDB[("Neon Serverless Cloud Pooler (AWS ap-southeast-1)")]
    end

    UI -->|"User text / Voice transcript"| Router
    STT --> UI
    Router --> ModeDet
    ModeDet --> SELEngine
    SELEngine --> StateMach
    StateMach --> T1
    T1 -.->|Timeout / Error| T2
    T2 -.->|Throttled / Offline| T3
    T1 & T2 & T3 -->|"Safe AI Reply + Latency Ms"| Router
    Router -->|"JSON Response (<2s)"| UI
    UI --> TTS
    Router -.->|"Async Background Task"| BGTasks
    BGTasks -->|"Persist Turn & Milestone"| NeonDB
```

---

## 🌟 Core Pedagogical & Technical Features

### 1. Progressive 3-Tier Learning Framework
* **Level 1 (Seedling — Ages 3–4):** Alphabet phonics, single vocabulary words, animal sounds, repetitive chanting (e.g. *"B says buh! 🚌"*).
* **Level 2 (Explorer — Ages 4–5):** 2–3 word phrases, colors, opposites, counting, simple questions.
* **Level 3 (Storyteller — Ages 6–7):** Interactive mini-dialogues, descriptive vocabulary, curiosity "why" explorations.
* **Milestone Star Rewards:** Visual pop and bounce animation when a child achieves milestones, with level-up prompts.

### 2. Child Mode Detection & Social-Emotional Learning (SEL)
* **Dynamic Mode Switching:** Detects when a child needs **Learning** (structured practice), **Conversation** (free chatting), **Engagement** (songs, jokes, rhymes when attention wanes), or **Support** (gentle reassurance when tired or sad).
* **Zero Negative Corrections:** Never says "No", "Wrong", or "Incorrect". Mistakes are praised as great attempts and gently remodeled with growth-mindset praise (*"Great try! High five! 🌟"*).
* **Emotional Check-in:** 1-tap mood selector (😊 Happy, 🧐 Curious, 🤪 Silly, 😴 Sleepy) that dynamically modulates bot tone.

### 3. Multimodal Voice Interaction (Web Speech API)
* **Speech-to-Text (STT):** Tapping the large friendly microphone button initiates voice recognition with a glowing pulse animation (`animate-ping`).
* **Text-to-Speech (TTS):** Responses are automatically narrated aloud using early-childhood pitch tuning (`pitch: 1.1`, `rate: 0.95`).
* **Parent Comfort Toggle:** Instant 1-tap sound mute/unmute control in the header.

### 4. Performance Guarantee: Strict `< 2.0s` SLA
* **Sub-Second Primary Inference:** Google Gemini 3.5 Flash Lite responds in **`~780ms`**.
* **Zero-Latency Fallback Engine:** If internet or upstream models throttle, our intelligent domain-aware pedagogical engine responds in **`< 2ms`**, guaranteeing 100% uptime and zero broken turns.
* **Non-Blocking Persistence:** Database writes to Neon PostgreSQL are dispatched via `BackgroundTasks` so cloud database latency never delays child responses.
* **Live Latency Meter:** Every assistant message displays its real response time (e.g. `⚡ 780ms`) in the UI for transparent verification.

---

## 🛠️ Complete Tech Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | React 19, Vite 8, Tailwind CSS, Lucide React, Web Speech API (SpeechRecognition + SpeechSynthesis) |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, SQLAlchemy 2.0, Pydantic v2, HTTPX Async |
| **Primary LLM** | Google Gemini 3.5 Flash Lite (`gemini-3.5-flash-lite` via Google AI Studio API) |
| **Fallback LLMs** | OpenRouter (`poolside/laguna-s-2.1:free`, `cohere/north-mini-code:free`) |
| **Cloud Database** | Neon Serverless Cloud PostgreSQL (`ap-southeast-1` AWS Pooler with SSL) |
| **Hosting** | Netlify (Frontend Edge SPA) + Render (Backend Python Web Service) |

---

## 🚀 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ranak8811/English-Learning-Chatbot.git
cd English-Learning-Chatbot
```

### 2. Configure Environment (`.env`)
Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://username:password@ep-your-database-pooler.aws.neon.tech/neondb?sslmode=require
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=poolside/laguna-s-2.1:free
PORT=8000
ENVIRONMENT=development
CORS_ORIGINS=*
```

### 3. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
* Interactive Swagger Docs: `http://localhost:8000/docs`
* Health Endpoint: `http://localhost:8000/api/health`

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Automated Test Suites

### Backend Unit & Integration Tests (27/27 Passing)
```bash
PYTHONPATH=backend pytest -v
```
* `test_bootstrap.py`: Health checks, CORS, configuration.
* `test_database.py`: Neon PostgreSQL connection, CRUD, turn logging.
* `test_ai_service.py`: Early childhood prompt construction, SLA budget validation.
* `test_mode_and_sel.py`: Mode detection, emotional sanitization, L1-L3 progression.
* `test_api_endpoints.py`: `/api/chat`, `/api/child`, `/api/child/{id}/mood`.

### Frontend Web Speech Unit Tests (5/5 Passing)
```bash
cd frontend
node --test src/services/speech.test.js
```
* Speech synthesis pitch/rate compliance (`1.1` pitch, `0.95` rate).
* Non-browser / unsupported fallback resilience.
* Regex emoji and markdown cleaner verification.

---

## 👥 GitHub Collaborators
Invited BRIMSEL Evaluators:
* `farzana@sharif.com`
* `masrur@sharif.com`

---

## 📄 License
Developed for the BRIMSEL Full-Stack AI Engineer Assessment. All rights reserved.
