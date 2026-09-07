import React, { useState } from 'react';
import { 
  GraduationCap, 
  MessageSquare, 
  Code2, 
  Bug,
  LogIn,
  LogOut,
  User as UserIcon
} from 'lucide-react';
import { signInWithGoogle, signOut, isSupabaseConfigured } from '../services/supabase';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  backendOnline,
  user,
  onOpenAuth
}) {
  const [showUserMenu, setShowUserMenu] = useState(false);

  const tabs = [
    { id: 'chat', label: 'AI Chat Tutor', icon: MessageSquare },
    { id: 'explain', label: 'Code Explanation', icon: Code2 },
    { id: 'debug', label: 'Debug Code', icon: Bug },
  ];

  const handleSignOut = async () => {
    try {
      setShowUserMenu(false);
      await signOut();
    } catch (err) {
      console.error('Sign out error:', err);
    }
  };

  const userAvatar = user?.user_metadata?.avatar_url || user?.user_metadata?.picture;
  const userName = user?.user_metadata?.full_name || user?.user_metadata?.name || user?.email?.split('@')[0] || 'Student';

  return (
    <header className="navbar">
      {/* Brand logo & title */}
      <div className="brand-section" onClick={() => setActiveTab('chat')}>
        <div className="brand-icon">
          <GraduationCap size={24} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span className="brand-title">Programming Tutor AI</span>
            <span className="brand-tag">Student Edition</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '2px' }}>
            <span style={{ 
              width: '7px', 
              height: '7px', 
              borderRadius: '50%', 
              backgroundColor: backendOnline ? '#10b981' : '#f43f5e',
              display: 'inline-block'
            }} />
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              {backendOnline ? 'AI Backend Ready' : 'Connecting to API...'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Workspace Navigation */}
      <nav className="nav-tabs">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              className={`nav-tab-btn ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Right controls: User Profile / Sign In / Sign Up */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div className="auth-section">
          {user ? (
            <div className="user-menu-container">
              <button 
                className="user-profile-btn"
                onClick={() => setShowUserMenu(!showUserMenu)}
                title={user.email}
              >
                {userAvatar ? (
                  <img src={userAvatar} alt="Avatar" className="user-avatar-img" />
                ) : (
                  <div className="user-avatar-placeholder">
                    {userName[0].toUpperCase()}
                  </div>
                )}
                <span className="user-name-label">{userName}</span>
              </button>

              {showUserMenu && (
                <div className="user-dropdown">
                  <div className="dropdown-header">
                    <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{userName}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{user.email}</div>
                  </div>
                  <div className="dropdown-divider" />
                  <button className="dropdown-item" onClick={handleSignOut}>
                    <LogOut size={14} />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button 
              className="btn-google-auth"
              onClick={onOpenAuth}
              title="Sign in or create an account"
            >
              <LogIn size={15} />
              <span>Sign In / Sign Up</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
