import React from 'react';
import { ArrowRight } from 'lucide-react';

export default function SuggestionChips({ suggestions, onSelectSuggestion, isProcessing }) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="suggestions-section">
      <div className="section-header">
        <span className="section-title">FOLLOW-UP QUERIES</span>
        <span style={{ fontSize: '10px', color: 'var(--color-muted)', fontFamily: 'var(--font-mono)' }}>
          N10
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {suggestions.map((s, idx) => (
          <button
            key={idx}
            className="suggestion-chip-btn"
            disabled={isProcessing}
            onClick={() => onSelectSuggestion(s)}
          >
            <span>{s.text}</span>
            <ArrowRight size={13} />
          </button>
        ))}
      </div>
    </div>
  );
}
