import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ChatTutor from './components/ChatTutor';
import CodeExplainer from './components/CodeExplainer';
import CodeDebugger from './components/CodeDebugger';
import AuthModal from './components/AuthModal';
import { api } from './services/api';
import { supabase, isSupabaseConfigured } from './services/supabase';
import { Sparkles } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [backendOnline, setBackendOnline] = useState(false);
  const [toast, setToast] = useState(null);
  const [user, setUser] = useState(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);

  const showToast = (message) => {
    setToast(message);
    setTimeout(() => {
      setToast(null);
    }, 3000);
  };

  // Monitor Supabase Authentication State
  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) return;

    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user || null);
    });

    // Subscribe to auth events (sign in, sign out, token refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setUser(session?.user || null);
        if (event === 'SIGNED_IN') {
          showToast(`Welcome back, ${session?.user?.user_metadata?.full_name || session?.user?.email}!`);
          setAuthModalOpen(false);
        } else if (event === 'SIGNED_OUT') {
          showToast('Signed out successfully.');
        }
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Check backend health on mount and periodically
  useEffect(() => {
    let isMounted = true;
    const checkConnection = async () => {
      try {
        await api.checkHealth();
        if (isMounted) setBackendOnline(true);
      } catch {
        if (isMounted) setBackendOnline(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 8000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendOnline={backendOnline}
        user={user}
        onOpenAuth={() => setAuthModalOpen(true)}
      />

      {/* Main View Area */}
      <main className="main-content">
        {activeTab === 'chat' && (
          <ChatTutor 
            user={user} 
            onOpenAuth={() => setAuthModalOpen(true)} 
          />
        )}

        {activeTab === 'explain' && (
          <CodeExplainer />
        )}

        {activeTab === 'debug' && (
          <CodeDebugger />
        )}
      </main>

      {/* Authentication Modal (Google OAuth & Email/Password) */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={(authedUser) => {
          setUser(authedUser);
          showToast(`Welcome, ${authedUser?.user_metadata?.full_name || authedUser?.email}!`);
        }}
      />

      {/* Floating Toast Notification */}
      {toast && (
        <div className="toast-msg">
          <Sparkles size={16} color="#818cf8" />
          <span>{toast}</span>
        </div>
      )}
    </div>
  );
}
