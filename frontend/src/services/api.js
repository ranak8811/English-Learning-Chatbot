import axios from 'axios';

// Base API URL supports local development and cloud production (Render)
const API_BASE =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD
    ? 'https://english-learning-chatbot-backend.onrender.com'
    : 'http://localhost:8000');

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

/**
 * Sends a message turn to the AI chatbot backend.
 */
export async function sendChatMessage({ message, childId, level, mood }) {
  const response = await client.post('/api/chat', {
    message,
    child_id: childId || null,
    current_level: level || 'L1',
    selected_mood: mood || 'happy',
  });
  return response.data;
}

/**
 * Initializes or fetches the child profile.
 */
export async function getOrCreateChildProfile(name = 'Little Explorer', age = 5, level = 'L1') {
  const response = await client.post('/api/child', {
    name,
    age,
    current_level: level,
  });
  return response.data;
}

/**
 * Retrieves child details including mastered words and star count.
 */
export async function fetchChildProfile(childId) {
  const response = await client.get(`/api/child/${childId}`);
  return response.data;
}

/**
 * Records an SEL mood check-in event.
 */
export async function recordChildMood(childId, mood) {
  const response = await client.post(`/api/child/${childId}/mood`, { mood });
  return response.data;
}

/**
 * Checks backend health and database connectivity.
 */
export async function checkBackendHealth() {
  const response = await client.get('/api/health');
  return response.data;
}
