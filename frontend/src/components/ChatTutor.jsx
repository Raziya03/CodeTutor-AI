import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Trash2, 
  Sparkles, 
  HelpCircle, 
  Lightbulb, 
  BookOpen, 
  Zap, 
  Code2, 
  MessageSquare,
  CheckCircle2
} from 'lucide-react';
import { api } from '../services/api';
import FormattedContent from './FormattedContent';
import HistorySidebar from './HistorySidebar';

const TUTOR_MODES = [
  { 
    id: 'learn', 
    label: 'Learn Concept', 
    icon: BookOpen, 
    desc: 'Teach step-by-step with code examples, takeaways & check question',
    placeholder: 'Ask about any concept (e.g. loops, recursion, OOP, data structures)...'
  },
  { 
    id: 'challenge', 
    label: 'Challenge Me', 
    icon: Zap, 
    desc: 'Solve coding challenges & get your attempts evaluated',
    placeholder: 'Ask for a challenge or paste your solution attempt...'
  },
  { 
    id: 'quiz', 
    label: 'Quiz Me', 
    icon: HelpCircle, 
    desc: 'One-by-one questions with immediate answer evaluations',
    placeholder: 'Answer the question (A, B, C, D) or ask to quiz on a topic...'
  },
  { 
    id: 'review', 
    label: 'Code Review', 
    icon: Code2, 
    desc: 'Analyze code for bugs, efficiency, and clean practices',
    placeholder: 'Paste your code for a detailed review and optimizations...'
  },
  { 
    id: 'chat', 
    label: 'General Tutor', 
    icon: MessageSquare, 
    desc: 'Open interactive programming Q&A',
    placeholder: 'Ask CodeTutor AI any programming question...'
  },
];

export default function ChatTutor({ user, onOpenAuth }) {
  const [mode, setMode] = useState('learn');
  
  const defaultWelcome = {
    role: 'assistant',
    content: `👋 Hi! I'm your **CodeTutor AI**.\n\nI provide structured, engaging learning tailored to what you need right now. Choose a mode above or ask any question:\n\n1. 💡 **Learn Concept**: Clear explanation, code snippet, key takeaways, and a check question.\n2. ⚡ **Challenge Me**: Practice coding problems and get your attempts evaluated.\n3. ❓ **Quiz Me**: One question at a time with immediate explanations.\n4. 🔍 **Code Review**: Analyze code for bugs, efficiency, and clean practices.\n\nNeed a clue anytime? Just click the **Need Hint** button below!\n\nWhat would you like to explore today?`,
    followups: [
      'Explain how loops work',
      'Teach me recursion with an example',
      'Give me a coding challenge',
      'Quiz me on Python basics',
    ],
  };

  const [messages, setMessages] = useState([defaultWelcome]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const messagesEndRef = useRef(null);

  const activeModeObj = TUTOR_MODES.find((m) => m.id === mode) || TUTOR_MODES[0];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load user conversations when user logs in or mounts
  const loadConversations = useCallback(async () => {
    if (!user) {
      setConversations([]);
      return;
    }
    setHistoryLoading(true);
    try {
      const data = await api.getConversations();
      setConversations(Array.isArray(data) ? data : []);
    } catch (err) {
      console.warn('Failed to load conversation history:', err);
    } finally {
      setHistoryLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Select and load past conversation
  const handleSelectConversation = async (id) => {
    if (id === activeConversationId) return;
    try {
      setLoading(true);
      const conv = await api.getConversation(id);
      setActiveConversationId(id);

      if (conv && conv.messages && conv.messages.length > 0) {
        setMessages(
          conv.messages.map((m) => ({
            role: m.role,
            content: m.content,
            followups: m.followups || [],
          }))
        );
      } else {
        setMessages([defaultWelcome]);
      }
    } catch (err) {
      console.error('Failed to load conversation messages:', err);
    } finally {
      setLoading(false);
    }
  };

  // Start fresh chat session
  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([defaultWelcome]);
  };

  // Delete conversation session
  const handleDeleteConversation = async (id) => {
    await api.deleteConversation(id);
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeConversationId === id) {
      handleNewChat();
    }
  };

  const handleSend = async (messageText, explicitMode = null) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || loading) return;

    const currentMode = explicitMode || mode;
    const userMessage = { role: 'user', content: textToSend };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const historyPayload = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await api.chat(
        textToSend,
        currentMode,
        historyPayload,
        activeConversationId
      );

      // If backend created or returned a new conversation session, update state
      if (res.conversation_id && res.conversation_id !== activeConversationId) {
        setActiveConversationId(res.conversation_id);
        loadConversations();
      }

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.reply,
          followups: res.suggested_followups || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ Oops! I encountered an error connecting to the tutor engine (${err.message}). Make sure the backend server is running on port 8000.`,
          followups: ['Try again', 'How do loops work?'],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleModeSelect = (newMode) => {
    setMode(newMode);
    if (newMode === 'challenge' && messages.length <= 2) {
      handleSend('Please give me a fun programming challenge to solve!', 'challenge');
    } else if (newMode === 'quiz' && messages.length <= 2) {
      handleSend('Please start a quiz with Question 1 on programming fundamentals!', 'quiz');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    handleNewChat();
  };

  return (
    <div className="chat-layout">
      {/* Conversation History Sidebar */}
      <HistorySidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
        user={user}
        loading={historyLoading}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
        onOpenAuth={onOpenAuth}
      />

      {/* Main Chat Work Area */}
      <div className="chat-container">
        {/* Workspace Header inside Chat */}
        <div className="pane-header" style={{ padding: '0.9rem 1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: '6px',
              background: 'var(--primary-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#818cf8',
            }}>
              <Bot size={18} />
            </div>
            <div>
              <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                CodeTutor AI
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Interactive Pedagogical Programming Assistant
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button
              className="btn-secondary"
              onClick={clearChat}
              style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
              title="Start a fresh chat"
            >
              <Trash2 size={13} />
              Clear
            </button>
          </div>
        </div>

        {/* 6 Tutor Modes Buttons Bar */}
        <div className="tutor-mode-bar">
          <span className="tutor-mode-label">Tutor Mode:</span>
          {TUTOR_MODES.map((m) => {
            const Icon = m.icon;
            const isActive = mode === m.id;
            return (
              <button
                key={m.id}
                className={`tutor-mode-btn mode-${m.id} ${isActive ? 'active' : ''}`}
                onClick={() => handleModeSelect(m.id)}
                title={m.desc}
              >
                <Icon size={14} />
                <span>{m.label}</span>
              </button>
            );
          })}
        </div>

        {/* Messages Scroll Area */}
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-bubble ${msg.role}`}>
              <div className={`chat-avatar ${msg.role === 'user' ? 'user-avatar' : ''}`}>
                {msg.role === 'assistant' ? (
                  <>
                    <Bot size={14} /> AI Tutor
                  </>
                ) : (
                  <>
                    <User size={14} /> You
                  </>
                )}
              </div>

              <FormattedContent text={msg.content} />

              {/* Followup suggestion chips */}
              {msg.followups && msg.followups.length > 0 && index === messages.length - 1 && !loading && (
                <div style={{ marginTop: '0.9rem', paddingTop: '0.6rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <HelpCircle size={12} /> Suggested follow-ups:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                    {msg.followups.map((tip, i) => (
                      <button
                        key={i}
                        className="prompt-chip"
                        onClick={() => handleSend(tip)}
                      >
                        {tip}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="chat-bubble assistant" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Bot size={16} className="empty-state-icon" style={{ width: 16, height: 16 }} />
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
                Tutor is crafting your structured response...
              </span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="chat-input-bar">
          <input
            type="text"
            className="chat-input"
            placeholder={activeModeObj.placeholder}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            type="button"
            className="btn-secondary"
            onClick={() => handleSend("I'm stuck, can you give me a progressive hint?", 'hint')}
            disabled={loading || messages.length <= 1}
            style={{ padding: '0.7rem 0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem', whiteSpace: 'nowrap', fontSize: '0.84rem' }}
            title="Ask for a progressive hint without spoiling the answer"
          >
            <Lightbulb size={15} style={{ color: '#fbbf24' }} />
            <span>Need Hint</span>
          </button>
          <button
            className="btn-primary"
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            style={{ padding: '0.7rem 1.25rem' }}
          >
            <Send size={16} />
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  );
}
