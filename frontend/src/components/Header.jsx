import React from 'react';
import { Satellite, Download, ArrowLeft } from 'lucide-react';

export default function Header({ onOpenReport, hasResult, onBackToLanding }) {
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
        <div className="brand-icon-wrapper" style={{ background: 'transparent', color: 'var(--color-ink)', border: 'none' }}>
          <Satellite size={20} strokeWidth={1.8} />
        </div>
        <div>
          <div className="brand-title" style={{ fontFamily: 'var(--font-land-display)', letterSpacing: '0.1em', fontWeight: 700 }}>
            <span style={{ color: '#ffffff' }}>SAT</span>
            <span style={{ color: 'var(--color-accent)' }}> QUERY</span>
          </div>
          <div className="brand-subtitle" style={{ letterSpacing: '0.05em' }}>
            Self-Adapting Multi-Modal Satellite Intelligence
          </div>
        </div>
      </div>

      <div className="system-telemetry-strip" style={{ gap: '16px' }}>
        <div className="telemetry-pill" style={{ border: 'none', background: 'transparent', padding: 0 }}>
          <span className="status-indicator" style={{ background: 'var(--status-success)', boxShadow: '0 0 6px var(--status-success)' }} />
          <span style={{ color: 'var(--color-muted)' }}>GSD: 10m AUTO</span>
        </div>
        <div className="telemetry-pill" style={{ border: 'none', background: 'transparent', padding: 0 }}>
          <span style={{ color: 'var(--color-muted)' }}>JEV-JEPA: ViT-768</span>
        </div>
        <div className="telemetry-pill" style={{ border: 'none', background: 'transparent', padding: 0 }}>
          <span style={{ color: 'var(--color-muted)' }}>SPEC: RS-VLM</span>
        </div>
        {hasResult && (
          <button
            onClick={onOpenReport}
            className="btn-workbench"
            style={{ padding: '6px 14px', fontSize: '11px', background: 'rgba(80,140,255,0.1)', color: '#fff', border: '1px solid rgba(80,140,255,0.3)', borderRadius: '4px' }}
          >
            <Download size={13} />
            <span style={{ letterSpacing: '0.05em', fontWeight: 600 }}>EXPORT</span>
          </button>
        )}
      </div>
    </header>
  );
}
