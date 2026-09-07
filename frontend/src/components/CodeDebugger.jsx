import React, { useState } from 'react';
import { 
  Bug, 
  CheckCircle2, 
  AlertTriangle, 
  Copy, 
  Check, 
  RotateCcw, 
  Sparkles,
  ShieldCheck,
  HelpCircle
} from 'lucide-react';
import { api } from '../services/api';

const BUGGY_PRESETS = [
  {
    name: 'Assignment in Condition',
    code: `def check_status(score):\n    if score = 100:\n        print("Perfect score!")\n    else:\n        print("Keep practicing!")\n\ncheck_status(100)`,
  },
  {
    name: 'Off-by-One Array Loop',
    code: `numbers = [10, 20, 30, 40]\n\n# Loop trying to access out-of-range index\nfor i in range(len(numbers) + 1):\n    print(numbers[i])`,
  },
  {
    name: 'Missing Colon in Function',
    code: `def calculate_average(grades)\n    total = sum(grades)\n    return total / len(grades)`,
  },
  {
    name: 'Infinite While Loop',
    code: `counter = 0\n\nwhile counter < 5:\n    print("Processing item...")\n    # Forgot to increment counter!`,
  },
];

export default function CodeDebugger({ difficulty = 'General' }) {
  const [code, setCode] = useState(BUGGY_PRESETS[0].code);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [apiError, setApiError] = useState(null);

  const handleDebug = async () => {
    if (!code.trim()) return;
    setLoading(true);
    setApiError(null);

    try {
      const data = await api.debug(code, 'auto', '', difficulty);
      setResult(data);
    } catch (err) {
      setApiError(err.message || 'Failed to analyze bugs.');
    } finally {
      setLoading(false);
    }
  };

  const loadPreset = (preset) => {
    setCode(preset.code);
    setResult(null);
  };

  const copyFixedCode = () => {
    if (result?.fixed_code) {
      navigator.clipboard.writeText(result.fixed_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Header Banner */}
      <div className="workspace-header">
        <div className="workspace-title-group">
          <h1>
            <Bug size={24} color="#f43f5e" />
            Debug Code
          </h1>
          <p>
            Paste your code in any language. The AI tutor diagnoses genuine errors and returns clean working code preserving your structure.
          </p>
        </div>

        {/* Buggy Presets */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Common Bugs:</span>
          {BUGGY_PRESETS.map((p, idx) => (
            <button
              key={idx}
              className="btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
              onClick={() => loadPreset(p)}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {/* Split Pane: Buggy Code Editor + Debug Diagnosis */}
      <div className="split-pane">
        {/* Left: Input Pane */}
        <div className="editor-pane">
          <div className="pane-header">
            <span className="pane-title">
              <Bug size={16} color="#f43f5e" /> Paste Code
            </span>
          </div>

          <textarea
            className="code-textarea"
            placeholder="Paste your code in any language (Python, C, C++, Java, JS, etc.)..."
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={12}
            spellCheck={false}
          />

          <div className="pane-footer">
            <button
              className="btn-secondary"
              onClick={() => {
                setCode('');
                setResult(null);
              }}
              disabled={!code}
            >
              <RotateCcw size={14} /> Clear
            </button>
            <button
              className="btn-primary"
              style={{ background: 'linear-gradient(135deg, #ef4444, #f43f5e)' }}
              onClick={handleDebug}
              disabled={loading || !code.trim()}
            >
              <Bug size={16} />
              <span>{loading ? 'Debugging Code...' : 'Diagnose & Fix Bugs'}</span>
            </button>
          </div>
        </div>

        {/* Right: Diagnosis & Fixed Code */}
        <div className="result-pane">
          {apiError && (
            <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid #f43f5e', borderRadius: '8px', color: '#fda4af' }}>
              <strong>Error:</strong> {apiError}
            </div>
          )}

          {!result && !loading && !apiError && (
            <div className="empty-state">
              <Bug className="empty-state-icon" style={{ color: '#f43f5e' }} />
              <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)' }}>Debugger Ready</h3>
              <p style={{ maxWidth: '340px', fontSize: '0.85rem' }}>
                Paste code on the left and click <strong>"Diagnose & Fix Bugs"</strong>. The AI detects genuine syntax, runtime, and logic errors.
              </p>
            </div>
          )}

          {loading && (
            <div className="empty-state">
              <Sparkles className="empty-state-icon" style={{ color: '#f43f5e', animation: 'spin 2s linear infinite' }} />
              <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)' }}>Analyzing Code & Error Traces...</h3>
              <p style={{ fontSize: '0.85rem' }}>Detecting syntax errors, runtime exceptions, and logic bugs.</p>
            </div>
          )}

          {result && !loading && (
            <>
              {/* Status & Error Type Card */}
              <div
                className="glass-card"
                style={{
                  padding: '1rem',
                  borderColor: result.has_bug ? 'rgba(244, 63, 94, 0.4)' : 'rgba(16, 185, 129, 0.4)',
                  background: result.has_bug ? 'rgba(244, 63, 94, 0.08)' : 'rgba(16, 185, 129, 0.08)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
                  {result.has_bug ? (
                    <AlertTriangle size={18} color="#f43f5e" />
                  ) : (
                    <CheckCircle2 size={18} color="#10b981" />
                  )}
                  <span style={{ fontWeight: 700, fontSize: '0.95rem', color: result.has_bug ? '#fca5a5' : '#86efac' }}>
                    {result.error_type}
                  </span>
                </div>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {result.root_cause}
                </p>
              </div>

              {/* Fixed Code Box */}
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <CheckCircle2 size={16} color="#10b981" /> {result.has_bug ? 'Corrected Code' : 'Verified Code'}
                  </span>
                  <button
                    className="copy-btn"
                    onClick={copyFixedCode}
                    style={{ background: 'rgba(255, 255, 255, 0.06)' }}
                  >
                    {copied ? (
                      <>
                        <Check size={13} color="#10b981" />
                        <span style={{ color: '#10b981' }}>Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy size={13} />
                        <span>Copy Code</span>
                      </>
                    )}
                  </button>
                </div>

                <div className="code-block" style={{ margin: 0 }}>
                  <div className="code-block-header">
                    <span>{result.language && result.language.toLowerCase() !== 'auto' ? result.language : 'Clean Working Code'}</span>
                    <span style={{ color: '#10b981' }}>✓ Verified</span>
                  </div>
                  <pre className="code-content">
                    <code>{result.fixed_code}</code>
                  </pre>
                </div>
              </div>

              {/* Tutor Explanation */}
              <div className="glass-card" style={{ padding: '1rem' }}>
                <h4 style={{ fontSize: '0.88rem', fontWeight: 700, color: '#e0e7ff', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <HelpCircle size={15} color="#818cf8" /> Why this fix works
                </h4>
                <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {result.explanation}
                </p>
              </div>

              {/* Prevention Tips */}
              {result.prevention_tips && result.prevention_tips.length > 0 && (
                <div className="glass-card" style={{ padding: '1rem', background: 'rgba(16, 185, 129, 0.05)', borderColor: 'rgba(16, 185, 129, 0.2)' }}>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.5rem' }}>
                    <ShieldCheck size={16} /> Bug Prevention Habits
                  </h4>
                  <ul style={{ paddingLeft: '1.25rem', fontSize: '0.84rem', color: '#d1fae5', lineHeight: 1.6 }}>
                    {result.prevention_tips.map((tip, idx) => (
                      <li key={idx}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
