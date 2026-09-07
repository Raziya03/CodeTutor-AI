import React, { useState } from 'react';
import { 
  X, 
  Mail, 
  Lock, 
  User, 
  ArrowRight, 
  CheckCircle, 
  AlertCircle, 
  Eye, 
  EyeOff, 
  Sparkles,
  Inbox
} from 'lucide-react';
import { 
  signInWithGoogle, 
  signUpWithEmail, 
  signInWithEmail, 
  resetPassword, 
  isSupabaseConfigured 
} from '../services/supabase';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [tab, setTab] = useState('signin'); // 'signin' | 'signup' | 'forgot'
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [confirmationSentEmail, setConfirmationSentEmail] = useState(null);
  const [resetSent, setResetSent] = useState(false);

  if (!isOpen) return null;

  const resetFormState = () => {
    setErrorMsg(null);
    setConfirmationSentEmail(null);
    setResetSent(false);
    setLoading(false);
  };

  const handleTabSwitch = (newTab) => {
    setTab(newTab);
    resetFormState();
  };

  // Google OAuth sign-in / sign-up
  const handleGoogleAuth = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      await signInWithGoogle();
      // Browser redirects to Google consent
    } catch (err) {
      setErrorMsg(err.message || 'Failed to initialize Google Sign In');
      setLoading(false);
    }
  };

  // Email/Password Submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);

    if (!email.trim() || (!password && tab !== 'forgot')) {
      setErrorMsg('Please fill in all required fields.');
      return;
    }

    if (tab === 'signup' && password.length < 6) {
      setErrorMsg('Password must be at least 6 characters long.');
      return;
    }

    try {
      setLoading(true);

      if (tab === 'signup') {
        const data = await signUpWithEmail(email.trim(), password, fullName.trim());
        // If Supabase requires email confirmation, session is null and user is returned
        if (data?.user && !data?.session) {
          setConfirmationSentEmail(email.trim());
        } else {
          // Auto-confirmed or existing session
          if (onAuthSuccess) onAuthSuccess(data?.user);
          onClose();
        }
      } else if (tab === 'signin') {
        const data = await signInWithEmail(email.trim(), password);
        if (onAuthSuccess) onAuthSuccess(data?.user);
        onClose();
      } else if (tab === 'forgot') {
        await resetPassword(email.trim());
        setResetSent(true);
      }
    } catch (err) {
      setErrorMsg(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div 
        className="modal-content auth-modal-box" 
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button 
          className="modal-close-btn" 
          onClick={onClose}
          aria-label="Close"
        >
          <X size={18} />
        </button>

        {/* Confirmation Email Sent Screen */}
        {confirmationSentEmail ? (
          <div className="auth-confirmation-screen">
            <div className="confirmation-icon-wrap">
              <Inbox size={36} color="#818cf8" />
            </div>
            <h3>Verify Your Email</h3>
            <p className="confirmation-desc">
              We have sent a verification link to:
              <br />
              <strong style={{ color: '#e0e7ff', wordBreak: 'break-all' }}>{confirmationSentEmail}</strong>
            </p>
            <div className="confirmation-alert">
              <Mail size={16} color="#34d399" />
              <span>
                Please check your inbox (or Spam folder) and click <strong>"Confirm your mail"</strong> to activate your CodeTutor account.
              </span>
            </div>
            <button 
              className="btn-primary" 
              style={{ width: '100%', marginTop: '1rem' }}
              onClick={() => {
                setConfirmationSentEmail(null);
                setTab('signin');
              }}
            >
              Return to Sign In
            </button>
          </div>
        ) : resetSent ? (
          <div className="auth-confirmation-screen">
            <div className="confirmation-icon-wrap">
              <CheckCircle size={36} color="#10b981" />
            </div>
            <h3>Password Reset Link Sent</h3>
            <p className="confirmation-desc">
              We've emailed a password reset link to:
              <br />
              <strong style={{ color: '#e0e7ff' }}>{email}</strong>
            </p>
            <button 
              className="btn-primary" 
              style={{ width: '100%', marginTop: '1rem' }}
              onClick={() => {
                setResetSent(false);
                setTab('signin');
              }}
            >
              Back to Sign In
            </button>
          </div>
        ) : (
          <>
            {/* Modal Header */}
            <div className="auth-header">
              <div className="auth-brand-badge">
                <Sparkles size={18} color="#818cf8" />
              </div>
              <h2>
                {tab === 'signin' && 'Welcome Back'}
                {tab === 'signup' && 'Create Your Account'}
                {tab === 'forgot' && 'Reset Password'}
              </h2>
              <p>
                {tab === 'signin' && 'Sign in to sync your tutor chats, challenges, and progress.'}
                {tab === 'signup' && 'Get started with personalized AI programming tutoring.'}
                {tab === 'forgot' && 'Enter your email to receive a password reset link.'}
              </p>
            </div>

            {/* Tab Switcher (Sign In vs Sign Up) */}
            {tab !== 'forgot' && (
              <div className="auth-tab-bar">
                <button
                  type="button"
                  className={`auth-tab-btn ${tab === 'signin' ? 'active' : ''}`}
                  onClick={() => handleTabSwitch('signin')}
                >
                  Sign In
                </button>
                <button
                  type="button"
                  className={`auth-tab-btn ${tab === 'signup' ? 'active' : ''}`}
                  onClick={() => handleTabSwitch('signup')}
                >
                  Create Account
                </button>
              </div>
            )}

            {/* Error Message Box */}
            {errorMsg && (
              <div className="auth-error-box">
                <AlertCircle size={16} />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Setup Notice if Supabase not configured */}
            {!isSupabaseConfigured && (
              <div className="auth-notice-box">
                <strong>Supabase Setup Needed:</strong> Add your <code>VITE_SUPABASE_URL</code> & <code>VITE_SUPABASE_ANON_KEY</code> to <code>frontend/.env</code> to activate live authentication.
              </div>
            )}

            {/* Google OAuth Button */}
            {tab !== 'forgot' && (
              <div style={{ marginBottom: '1.25rem' }}>
                <button
                  type="button"
                  className="btn-google-auth-full"
                  onClick={handleGoogleAuth}
                  disabled={loading}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                  </svg>
                  <span>{tab === 'signup' ? 'Sign up with Google' : 'Continue with Google'}</span>
                </button>

                <div className="auth-divider">
                  <span>or continue with email</span>
                </div>
              </div>
            )}

            {/* Email & Password Form */}
            <form onSubmit={handleSubmit} className="auth-form">
              {tab === 'signup' && (
                <div className="form-group">
                  <label>Full Name</label>
                  <div className="input-with-icon">
                    <User size={16} className="input-icon" />
                    <input
                      type="text"
                      className="auth-input"
                      placeholder="e.g. Alex Johnson"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      disabled={loading}
                    />
                  </div>
                </div>
              )}

              <div className="form-group">
                <label>Email Address</label>
                <div className="input-with-icon">
                  <Mail size={16} className="input-icon" />
                  <input
                    type="email"
                    required
                    className="auth-input"
                    placeholder="you@gmail.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>

              {tab !== 'forgot' && (
                <div className="form-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <label>Password</label>
                    {tab === 'signin' && (
                      <button
                        type="button"
                        className="btn-link"
                        onClick={() => handleTabSwitch('forgot')}
                      >
                        Forgot password?
                      </button>
                    )}
                  </div>
                  <div className="input-with-icon">
                    <Lock size={16} className="input-icon" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      className="auth-input"
                      placeholder={tab === 'signup' ? 'At least 6 characters' : 'Enter your password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      disabled={loading}
                    />
                    <button
                      type="button"
                      className="password-toggle-btn"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                    </button>
                  </div>
                </div>
              )}

              <button
                type="submit"
                className="btn-primary auth-submit-btn"
                disabled={loading}
              >
                <span>
                  {loading
                    ? 'Processing...'
                    : tab === 'signup'
                    ? 'Create Account'
                    : tab === 'signin'
                    ? 'Sign In'
                    : 'Send Reset Link'}
                </span>
                <ArrowRight size={16} />
              </button>
            </form>

            {/* Footer switcher */}
            <div className="auth-footer">
              {tab === 'signin' && (
                <p>
                  Don't have an account?{' '}
                  <button type="button" className="btn-link" onClick={() => handleTabSwitch('signup')}>
                    Sign up
                  </button>
                </p>
              )}
              {tab === 'signup' && (
                <p>
                  Already have an account?{' '}
                  <button type="button" className="btn-link" onClick={() => handleTabSwitch('signin')}>
                    Sign in
                  </button>
                </p>
              )}
              {tab === 'forgot' && (
                <p>
                  Remember your password?{' '}
                  <button type="button" className="btn-link" onClick={() => handleTabSwitch('signin')}>
                    Back to Sign In
                  </button>
                </p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
