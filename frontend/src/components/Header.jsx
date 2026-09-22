import React from 'react';
import { Satellite, Download } from 'lucide-react';

export default function Header({ onOpenReport, hasResult }) {
  return (
    <header className="top-header">
      <div className="brand-section">
        <div className="brand-icon-wrapper">
          <Satellite size={20} />
        </div>
        <div>
          <div className="brand-title">
            SATQUERY AI
            <span className="brand-badge">PROTOTYPE</span>
          </div>
          <div className="brand-subtitle">
            Remote Sensing Visual Question Answering Workbench
          </div>
        </div>
      </div>

      <div className="system-telemetry-strip">
        <div className="telemetry-pill active">
          <span className="status-indicator" />
          <span>GSD: 10m AUTO</span>
        </div>
        <div className="telemetry-pill active">
          <span>JEV-JEPA: ViT-768</span>
        </div>
        <div className="telemetry-pill active">
          <span>SPEC: RS-VLM</span>
        </div>
        {hasResult && (
          <button
            onClick={onOpenReport}
            className="btn-workbench"
            style={{ padding: '4px 12px', fontSize: '11px' }}
          >
            <Download size={12} />
            <span>EXPORT</span>
          </button>
        )}
      </div>
    </header>
  );
}
