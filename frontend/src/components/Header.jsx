import React from 'react';
import { Satellite, Download, ArrowLeft } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

export default function Header({ onOpenReport, hasResult, onBackToLanding, theme, onToggleTheme }) {
  return (
    <header className="top-header">
      <div className="brand-section">
        {onBackToLanding && (
          <button
            onClick={onBackToLanding}
            className="btn-workbench back-btn"
            title="Return to landing page"
            aria-label="Back to home"
            style={{ padding: '6px 10px', marginRight: '4px', background: 'transparent', border: 'none' }}
          >
            <ArrowLeft size={14} />
          </button>
        )}
        <div className="brand-icon-wrapper" style={{ background: 'transparent', color: 'var(--color-accent)', border: 'none' }}>
          <Satellite size={20} strokeWidth={1.8} />
        </div>
        <div>
          <div className="brand-title" style={{ fontFamily: 'var(--font-land-display)', letterSpacing: '0.1em', fontWeight: 700 }}>
            <span className="brand-sat-text">SAT</span>
            <span style={{ color: 'var(--color-accent)' }}> QUERY</span>
          </div>
          <div className="brand-subtitle" style={{ letterSpacing: '0.05em' }}>
            Self-Adapting Multi-Modal Satellite Intelligence
          </div>
        </div>
      </div>

      <div className="system-telemetry-strip" style={{ gap: '12px', alignItems: 'center' }}>
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />

        {hasResult && (
          <button
            onClick={onOpenReport}
            className="btn-workbench btn-primary"
            style={{ padding: '6px 14px', fontSize: '11px', borderRadius: '4px' }}
          >
            <Download size={13} />
            <span style={{ letterSpacing: '0.05em', fontWeight: 600 }}>EXPORT</span>
          </button>
        )}
      </div>
    </header>
  );
}
