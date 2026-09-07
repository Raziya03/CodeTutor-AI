import React, { useState } from 'react';
import { Check, Copy } from 'lucide-react';

// Clean raw LaTeX & mathematical artifacts into friendly Unicode symbols
function sanitizeContent(rawText) {
  if (!rawText) return '';
  return rawText
    .replace(/\$\\rightarrow\$/g, '→')
    .replace(/\$\\leftarrow\$/g, '←')
    .replace(/\\rightarrow/g, '→')
    .replace(/\\leftarrow/g, '←')
    .replace(/\$\\to\$/g, '→')
    .replace(/\\to/g, '→')
    .replace(/\\le(q)?\b/g, '≤')
    .replace(/\\ge(q)?\b/g, '≥')
    .replace(/\\ne(q)?\b/g, '≠')
    .replace(/\\times\b/g, '×')
    .replace(/\\approx\b/g, '≈')
    .replace(/\\cdot\b/g, '·')
    .replace(/\\sqrt\{([^}]+)\}/g, '√($1)')
    .replace(/\\sqrt\b/g, '√')
    .replace(/\\log\b/g, 'log')
    .replace(/\\ln\b/g, 'ln')
    .replace(/\\lg\b/g, 'lg')
    .replace(/\\infty\b/g, '∞')
    .replace(/\\sum\b/g, '∑')
    .replace(/\\prod\b/g, '∏')
    .replace(/\\pm\b/g, '±')
    .replace(/\\text\{([^}]+)\}/g, '$1')
    // Remove raw dollar signs around math expressions like $N$, $N - 1$, $0$
    .replace(/\$([^$\n]+)\$/g, '$1')
    // Clean remaining backslashes before common identifiers (e.g. \log, \theta)
    .replace(/\\([a-zA-Z]+)/g, '$1');
}

export default function FormattedContent({ text }) {
  const [copiedIndex, setCopiedIndex] = useState(null);

  if (!text) return null;

  // Auto-close unclosed markdown code blocks if truncated
  let processedText = sanitizeContent(text);
  const fenceMatches = processedText.match(/```/g);
  if (fenceMatches && fenceMatches.length % 2 !== 0) {
    processedText += '\n```';
  }

  // Split by code blocks ```...```
  const parts = processedText.split(/(```[\s\S]*?```)/g);

  const handleCopy = (codeText, idx) => {
    navigator.clipboard.writeText(codeText);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div>
      {parts.map((part, idx) => {
        if (part.startsWith('```') && part.endsWith('```')) {
          // Extract language and code
          const firstLineEnd = part.indexOf('\n');
          let lang = 'code';
          let code = '';
          if (firstLineEnd !== -1) {
            lang = part.slice(3, firstLineEnd).trim() || 'code';
            code = part.slice(firstLineEnd + 1, -3);
          } else {
            code = part.slice(3, -3);
          }

          return (
            <div key={idx} className="code-block" style={{ margin: '0.6rem 0' }}>
              <div className="code-block-header">
                <span>{lang}</span>
                <button
                  className="copy-btn"
                  onClick={() => handleCopy(code, idx)}
                  title="Copy code to clipboard"
                >
                  {copiedIndex === idx ? (
                    <>
                      <Check size={12} color="#10b981" />
                      <span style={{ color: '#10b981' }}>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy size={12} />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
              <pre className="code-content">
                <code>{code}</code>
              </pre>
            </div>
          );
        }

        // Format basic markdown elements: headings, blockquotes, bullets, bold
        const lines = part.split('\n');
        return (
          <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {lines.map((line, lineIdx) => {
              if (!line.trim()) return <div key={lineIdx} style={{ height: '0.25rem' }} />;

              // Headings: matches #, ##, ###, ####, #####, ###### cleanly without leaving hashes
              const headingMatch = line.match(/^(#{1,6})\s*(.*)/);
              if (headingMatch) {
                const level = headingMatch[1].length;
                const content = headingMatch[2];
                if (level === 1 || level === 2) {
                  return (
                    <h3 key={lineIdx} style={{ fontSize: '1.08rem', fontWeight: 700, margin: '0.55rem 0 0.2rem', color: '#f8fafc' }}>
                      {renderInline(content)}
                    </h3>
                  );
                }
                if (level === 3) {
                  return (
                    <h4 key={lineIdx} style={{ fontSize: '0.98rem', fontWeight: 700, margin: '0.45rem 0 0.15rem', color: '#f1f5f9' }}>
                      {renderInline(content)}
                    </h4>
                  );
                }
                return (
                  <h4 key={lineIdx} style={{ fontSize: '0.92rem', fontWeight: 600, margin: '0.35rem 0 0.15rem', color: '#e2e8f0' }}>
                    {renderInline(content)}
                  </h4>
                );
              }

              // Blockquotes
              if (line.startsWith('> ')) {
                return (
                  <blockquote
                    key={lineIdx}
                    style={{
                      borderLeft: '3px solid #6366f1',
                      paddingLeft: '0.75rem',
                      color: '#cbd5e1',
                      fontStyle: 'italic',
                      margin: '0.3rem 0',
                    }}
                  >
                    {renderInline(line.replace('> ', ''))}
                  </blockquote>
                );
              }

              // Bullets
              if (line.startsWith('- ') || line.startsWith('* ')) {
                return (
                  <div key={lineIdx} style={{ display: 'flex', gap: '0.5rem', paddingLeft: '0.5rem' }}>
                    <span style={{ color: '#818cf8' }}>•</span>
                    <span>{renderInline(line.slice(2))}</span>
                  </div>
                );
              }

              // Numbered list
              const numMatch = line.match(/^(\d+\.)\s+(.*)/);
              if (numMatch) {
                return (
                  <div key={lineIdx} style={{ display: 'flex', gap: '0.5rem', paddingLeft: '0.5rem' }}>
                    <span style={{ color: '#818cf8', fontWeight: 600 }}>{numMatch[1]}</span>
                    <span>{renderInline(numMatch[2])}</span>
                  </div>
                );
              }

              return <p key={lineIdx}>{renderInline(line)}</p>;
            })}
          </div>
        );
      })}
    </div>
  );
}

// Render bold (`**text**`), inline code (`` `code` ``), and italics (`*text*` / `_text_`)
function renderInline(text) {
  const parts = text.split(/(\*\*.*?\*\*|`.*?`|\*[^*\n]+?\*|_[^_\n]+?_)/g);
  return parts.map((chunk, i) => {
    if (!chunk) return null;
    if (chunk.startsWith('**') && chunk.endsWith('**') && chunk.length >= 4) {
      return <strong key={i} style={{ color: '#ffffff' }}>{chunk.slice(2, -2)}</strong>;
    }
    if (chunk.startsWith('`') && chunk.endsWith('`') && chunk.length >= 2) {
      return (
        <code
          key={i}
          style={{
            background: 'rgba(0, 0, 0, 0.4)',
            padding: '2px 6px',
            borderRadius: '4px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.85em',
            color: '#38bdf8',
          }}
        >
          {chunk.slice(1, -1)}
        </code>
      );
    }
    if (
      (chunk.startsWith('*') && chunk.endsWith('*') && chunk.length >= 2) ||
      (chunk.startsWith('_') && chunk.endsWith('_') && chunk.length >= 2)
    ) {
      return (
        <em key={i} style={{ color: '#cbd5e1', fontStyle: 'italic' }}>
          {chunk.slice(1, -1)}
        </em>
      );
    }
    return chunk;
  });
}
