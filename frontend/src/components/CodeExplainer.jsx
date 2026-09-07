import React, { useState } from 'react';
import { 
  Code2, 
  Sparkles, 
  Clock, 
  Database, 
  Layers, 
  Lightbulb, 
  RotateCcw,
  BookOpen
} from 'lucide-react';
import { api } from '../services/api';

const SAMPLE_PRESETS = [
  {
    name: 'Binary Search',
    code: `def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return -1`,
  },
  {
    name: 'Fibonacci Memoization',
    code: `memo = {}

def fib(n):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fib(n - 1) + fib(n - 2)
    return memo[n]`,
  },
  {
    name: 'Palindrome Checker',
    code: `function isPalindrome(str) {
  const cleanStr = str.toLowerCase().replace(/[^a-z0-9]/g, '');
  let left = 0;
  let right = cleanStr.length - 1;
  
  while (left < right) {
    if (cleanStr[left] !== cleanStr[right]) {
      return false;
    }
    left++;
    right--;
  }
  return true;
}`,
  },
];

export default function CodeExplainer({ difficulty = 'General' }) {
  const [code, setCode] = useState(SAMPLE_PRESETS[0].code);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleExplain = async () => {
    if (!code.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const data = await api.explain(code, 'auto', difficulty);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to explain code.');
    } finally {
      setLoading(false);
    }
  };

  const loadPreset = (preset) => {
    setCode(preset.code);
    setResult(null);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Banner */}
      <div className="workspace-header">
        <div className="workspace-title-group">
          <h1>
            <Code2 size={24} color="#818cf8" />
            Code Explanation
          </h1>
          <p>
            Paste your code in any language to get a friendly, line-by-line breakdown, concept tags, and complexity analysis.
          </p>
        </div>

        {/* Preset quick buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Load Sample:</span>
          {SAMPLE_PRESETS.map((p, idx) => (
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

      {/* Split Pane: Code Editor + Explanation */}
      <div className="split-pane">
        {/* Left: Input Pane */}
        <div className="editor-pane">
          <div className="pane-header">
            <span className="pane-title">
              <Code2 size={16} /> Source Code
            </span>
          </div>

          <textarea
            className="code-textarea"
            placeholder="Paste or write any code snippet here in any language..."
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={14}
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
              onClick={handleExplain}
              disabled={loading || !code.trim()}
            >
              <Sparkles size={16} />
              <span>{loading ? 'Analyzing Code...' : 'Explain Code'}</span>
            </button>
          </div>
        </div>

        {/* Right: Explanation Result Pane */}
        <div className="result-pane">
          {error && (
            <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid #f43f5e', borderRadius: '8px', color: '#fda4af' }}>
              <strong>Error:</strong> {error}
            </div>
          )}

          {!result && !loading && !error && (
            <div className="empty-state">
              <BookOpen className="empty-state-icon" />
              <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)' }}>No Explanation Yet</h3>
              <p style={{ maxWidth: '340px', fontSize: '0.85rem' }}>
                Paste code on the left and click <strong>"Explain Code"</strong> to receive a structured breakdown, complexity scores, and line-by-line annotations.
              </p>
            </div>
          )}

          {loading && (
            <div className="empty-state">
              <Sparkles className="empty-state-icon" style={{ animation: 'spin 2s linear infinite' }} />
              <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)' }}>Analyzing Code Structure...</h3>
              <p style={{ fontSize: '0.85rem' }}>Breaking down logic, loops, and time complexity.</p>
            </div>
          )}

          {result && !loading && (
            <>
              {/* Summary Card */}
              <div className="glass-card" style={{ padding: '1.1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#e0e7ff', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Sparkles size={16} color="#818cf8" /> High-Level Overview
                  </h3>
                </div>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {result.summary}
                </p>
              </div>

              {/* Complexity & Concepts Metrics */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.75rem' }}>
                <div className="glass-card" style={{ padding: '0.75rem 1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                    <Clock size={14} color="#06b6d4" /> Time Complexity
                  </div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#38bdf8', marginTop: '0.2rem' }}>
                    {result.time_complexity}
                  </div>
                </div>

                <div className="glass-card" style={{ padding: '0.75rem 1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                    <Database size={14} color="#a855f7" /> Space Complexity
                  </div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#c084fc', marginTop: '0.2rem' }}>
                    {result.space_complexity}
                  </div>
                </div>
              </div>

              {/* Core Concepts */}
              {result.concepts && result.concepts.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <Layers size={13} /> Key Concepts:
                  </span>
                  {result.concepts.map((concept, i) => (
                    <span
                      key={i}
                      style={{
                        fontSize: '0.75rem',
                        padding: '2px 8px',
                        borderRadius: '6px',
                        background: 'rgba(99, 102, 241, 0.15)',
                        border: '1px solid rgba(99, 102, 241, 0.3)',
                        color: '#a5b4fc',
                        fontWeight: 500,
                      }}
                    >
                      {concept}
                    </span>
                  ))}
                </div>
              )}

              {/* Line-by-Line Section */}
              <div style={{ marginTop: '0.5rem' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#f1f5f9', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Code2 size={16} color="#818cf8" /> Line-by-Line Breakdown
                </h4>
                <div className="line-breakdown-list">
                  {result.line_by_line.map((item, i) => (
                    <div key={i} className="line-item">
                      <div className="line-code">
                        <span className="line-num">L{item.line_number}</span>
                        <code>{item.code}</code>
                      </div>
                      <div className="line-explanation">
                        {item.explanation}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Tutor Tips */}
              {result.tutor_tips && result.tutor_tips.length > 0 && (
                <div className="glass-card" style={{ padding: '1rem', background: 'rgba(245, 158, 11, 0.05)', borderColor: 'rgba(245, 158, 11, 0.2)' }}>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.5rem' }}>
                    <Lightbulb size={16} /> Tutor Tips & Best Practices
                  </h4>
                  <ul style={{ paddingLeft: '1.25rem', fontSize: '0.84rem', color: '#fef3c7', lineHeight: 1.6 }}>
                    {result.tutor_tips.map((tip, idx) => (
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
