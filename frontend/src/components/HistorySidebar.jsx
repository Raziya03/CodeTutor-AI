import React, { useState } from 'react';
import { 
  MessageSquare, 
  Plus, 
  Trash2, 
  ChevronLeft, 
  ChevronRight, 
  LogIn, 
  Sparkles,
  Clock
} from 'lucide-react';
import { signInWithGoogle, isSupabaseConfigured } from '../services/supabase';

export default function HistorySidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  user,
  loading,
  collapsed,
  setCollapsed,
  onOpenAuth
}) {
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation?')) {
      setDeletingId(id);
      try {
        await onDeleteConversation(id);
      } finally {
        setDeletingId(null);
      }
    }
  };

  if (collapsed) {
    return (
      <div className="history-sidebar-collapsed">
        <button 
          className="sidebar-toggle-btn"
          onClick={() => setCollapsed(false)}
          title="Open Conversation History"
        >
          <ChevronRight size={18} />
        </button>
        <button 
          className="sidebar-new-btn-icon"
          onClick={onNewChat}
          title="New Chat"
        >
          <Plus size={18} />
        </button>
      </div>
    );
  }

  return (
    <aside className="history-sidebar">
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Clock size={16} color="#818cf8" />
          <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>History</span>
        </div>
        <button 
          className="sidebar-toggle-btn"
          onClick={() => setCollapsed(true)}
          title="Collapse Sidebar"
        >
          <ChevronLeft size={18} />
        </button>
      </div>

      {/* New Chat Button */}
      <div style={{ padding: '0.75rem 1rem' }}>
        <button 
          className="btn-new-chat"
          onClick={onNewChat}
        >
          <Plus size={16} />
          <span>New Chat</span>
        </button>
      </div>

      {/* Conversation List */}
      <div className="sidebar-chat-list">
        {!user ? (
          <div className="sidebar-guest-notice">
            <Sparkles size={24} color="#818cf8" style={{ marginBottom: '0.5rem' }} />
            <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
              Save Your Learning History
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: '1.4', marginBottom: '0.75rem' }}>
              Sign in to automatically save your coding conversations and resume anytime across devices.
            </p>
            <button className="btn-google-sidebar" onClick={onOpenAuth}>
              <LogIn size={14} />
              <span>Sign In / Sign Up</span>
            </button>
          </div>
        ) : loading ? (
          <div style={{ padding: '1rem', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Loading past chats...
          </div>
        ) : conversations.length === 0 ? (
          <div style={{ padding: '1.5rem 1rem', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            No saved conversations yet. Start asking questions!
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeConversationId;
            return (
              <div
                key={conv.id}
                className={`sidebar-chat-item ${isActive ? 'active' : ''}`}
                onClick={() => onSelectConversation(conv.id)}
              >
                <MessageSquare size={14} className="chat-item-icon" />
                <div className="chat-item-info">
                  <div className="chat-item-title">{conv.title || 'New Chat'}</div>
                  <div className="chat-item-meta" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {conv.updated_at ? new Date(conv.updated_at).toLocaleDateString() : 'Recent'}
                  </div>
                </div>
                <button
                  className="chat-item-delete"
                  onClick={(e) => handleDelete(e, conv.id)}
                  disabled={deletingId === conv.id}
                  title="Delete chat"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}
