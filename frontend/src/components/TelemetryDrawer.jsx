import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

export default function TelemetryDrawer({ trace }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!trace || trace.length === 0) return null;

  const totalDuration = trace.reduce((sum, item) => sum + (item.duration_ms || 0), 0);

  return (
    <div>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="btn-workbench"
        style={{
          width: '100%',
          justifyContent: 'space-between',
          padding: 'var(--space-2) var(--space-3)',
          fontSize: '11px',
        }}
      >
        <span style={{ fontFamily: 'var(--font-mono)', fontVariantNumeric: 'tabular-nums' }}>
          PIPELINE TRACE ({totalDuration.toFixed(0)} ms)
        </span>
        {isOpen ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
      </button>

      {isOpen && (
        <div className="telemetry-stepper" style={{ marginTop: 'var(--space-2)' }}>
          {trace.map((step, idx) => (
            <div key={idx} className="stepper-item">
              <span className="stage-name">{step.stage}</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <span style={{ color: 'var(--color-muted)', fontVariantNumeric: 'tabular-nums' }}>
                  {step.duration_ms ? `${step.duration_ms.toFixed(0)} ms` : '--'}
                </span>
                <span className={`stage-badge ${step.status === 'ok' ? 'ok' : 'warn'}`}>
                  {step.status?.toUpperCase() || 'OK'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
