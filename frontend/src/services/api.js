import { getAccessToken } from './supabase';

const API_BASE = (
  import.meta.env.VITE_API_URL || 
  (import.meta.env.PROD ? '/api' : 'http://localhost:8000/api')
).replace(/\/+$/, '');

/**
 * Handle API fetch with bearer auth, error handling and fallback
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Inject Supabase JWT bearer token if user is signed in
  try {
    const token = await getAccessToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  } catch (e) {
    // Continue unauthenticated in guest mode
  }

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: 'Unknown error occurred' }));
      throw new Error(errData.detail || `Request failed with status ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error(`API Error on [${endpoint}]:`, error);
    throw error;
  }
}

export const api = {
  // Check backend connectivity
  checkHealth: () => request('/health'),

  // Current authenticated user
  getAuthProfile: () => request('/auth/me'),

  // AI Chat Tutor with mode and optional conversation_id
  chat: (message, mode = 'learn', history = [], conversationId = null) =>
    request('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        mode,
        history,
        conversation_id: conversationId,
      }),
    }),

  // Conversation history endpoints
  getConversations: () => request('/conversations'),

  createConversation: (title = 'New Chat', difficulty = 'beginner') =>
    request('/conversations', {
      method: 'POST',
      body: JSON.stringify({ title, difficulty }),
    }),

  getConversation: (id) => request(`/conversations/${id}`),

  deleteConversation: (id) =>
    request(`/conversations/${id}`, {
      method: 'DELETE',
    }),

  // Code Explanation
  explain: (code, language = 'python', difficulty = 'beginner') =>
    request('/explain', {
      method: 'POST',
      body: JSON.stringify({ code, language, difficulty }),
    }),

  // Debug Code
  debug: (code, language = 'python', errorMessage = '', difficulty = 'beginner') =>
    request('/debug', {
      method: 'POST',
      body: JSON.stringify({ code, language, error_message: errorMessage, difficulty }),
    }),
};
