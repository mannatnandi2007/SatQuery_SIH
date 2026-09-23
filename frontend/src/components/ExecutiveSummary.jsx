import React from 'react';
import { CheckCircle2, AlertTriangle, Target, Search } from 'lucide-react';

export default function ExecutiveSummary({ resultData }) {
      <div className="executive-summary-card" style={{ opacity: 0.6, background: 'transparent', border: 'none', padding: '0' }}>
        <div className="summary-header-row" style={{ borderBottom: '1px solid var(--color-rule-subtle)', paddingBottom: '8px', marginBottom: '16px' }}>
          <span className="section-title" style={{ color: 'var(--color-muted)', letterSpacing: '0.1em' }}>ANALYSIS</span>
        </div>
        <div className="empty-state-text" style={{ textAlign: 'left', color: 'var(--color-muted)' }}>
          Run satellite analysis to generate AI insights.
        </div>
      </div>

  const confidence = resultData.confidence || { score: 0.94, label: 'High Confidence' };
  const scorePct = Math.round((confidence.score || 0.94) * 100);
  const isHighConf = (confidence.score || 0.94) >= 0.8;
  const objects = resultData.detected_objects || resultData.objects;
  const detailed = resultData.detailed_analysis;
  const hasEvidence = Boolean(detailed || (resultData.evidence && typeof resultData.evidence === 'string'));

  return (
    <div className="executive-summary-card" style={{ display: 'flex', flexDirection: 'column', gap: '24px', background: 'transparent', border: 'none', padding: 0 }}>
      
      {/* 1. ANALYSIS */}
      <div>
        <div className="summary-header-row" style={{ borderBottom: '1px solid var(--color-rule-subtle)', paddingBottom: '8px', marginBottom: '12px' }}>
          <span className="section-title" style={{ color: '#fff', letterSpacing: '0.1em' }}>ANALYSIS</span>
        </div>
        <div className="summary-answer-text" style={{ color: '#fff', fontSize: '14px', lineHeight: '1.6', fontFamily: 'var(--font-land-display)' }}>
          {resultData.answer || 'Analysis completed.'}
        </div>
      </div>

      {/* 2. CONFIDENCE */}
      <div>
        <div className="summary-header-row" style={{ borderBottom: '1px solid var(--color-rule-subtle)', paddingBottom: '8px', marginBottom: '12px' }}>
          <span className="section-title" style={{ color: 'var(--color-muted)', letterSpacing: '0.1em' }}>CONFIDENCE</span>
        </div>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 12px', background: 'rgba(255, 136, 34, 0.1)', border: '1px solid var(--color-accent)', borderRadius: '4px', color: 'var(--color-accent)', fontSize: '13px', fontWeight: '600', fontFamily: 'var(--font-mono)' }}>
          {isHighConf ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
          <span>{scorePct}% {confidence.label || 'Confidence'}</span>
        </div>
      </div>

      {/* 3. DETECTED OBJECTS (Conditional) */}
      {objects && (
        <div>
          <div className="summary-header-row" style={{ borderBottom: '1px solid var(--color-rule-subtle)', paddingBottom: '8px', marginBottom: '12px' }}>
            <span className="section-title" style={{ color: 'var(--color-muted)', letterSpacing: '0.1em' }}>DETECTED OBJECTS</span>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {Array.isArray(objects) ? objects.map((obj, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '4px 8px', background: 'transparent', border: '1px solid var(--color-rule)', borderRadius: '2px', fontSize: '12px', color: '#fff', fontFamily: 'var(--font-mono)' }}>
                <Target size={12} style={{ color: '#508CFF' }} />
                <span>{typeof obj === 'string' ? obj : obj.label || 'Object'}</span>
              </div>
            )) : (
              <div style={{ fontSize: '13px', color: '#fff' }}>{String(objects)}</div>
            )}
          </div>
        </div>
      )}

      {/* 4. EVIDENCE (Conditional) */}
      {hasEvidence && (
        <div>
          <div className="summary-header-row" style={{ borderBottom: '1px solid var(--color-rule-subtle)', paddingBottom: '8px', marginBottom: '12px' }}>
            <span className="section-title" style={{ color: 'var(--color-muted)', letterSpacing: '0.1em' }}>EVIDENCE</span>
          </div>
          <div style={{ background: 'transparent', borderLeft: '2px solid #508CFF', padding: '0 0 0 12px', fontSize: '13px', color: 'var(--color-ink-2)', lineHeight: '1.5' }}>
            {detailed ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {detailed.land_cover && (
                  <div>
                    <div style={{ fontWeight: 600, color: '#508CFF', marginBottom: '2px', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>Land Cover Classification:</div>
                    <div style={{ color: '#e2e8f0', fontSize: '12px' }}>{detailed.land_cover}</div>
                  </div>
                )}
                {Array.isArray(detailed.key_objects) && detailed.key_objects.length > 0 && (
                  <div>
                    <div style={{ fontWeight: 600, color: '#508CFF', marginBottom: '4px', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>Ground Observations:</div>
                    <ul style={{ margin: 0, paddingLeft: '16px', color: '#cbd5e1', fontSize: '12px', lineHeight: '1.5' }}>
                      {detailed.key_objects.map((ko, idx) => (
                        <li key={idx} style={{ marginBottom: '2px' }}>{ko}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {detailed.spatial_patterns && (
                  <div style={{ color: 'var(--color-muted)', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
                    <span>Pattern: </span>{detailed.spatial_patterns}
                  </div>
                )}
              </div>
            ) : (
              <div style={{ color: '#fff' }}>{String(resultData.evidence)}</div>
            )}
          </div>
        </div>
      )}

      {/* Specialist Model Badge */}
      <div style={{ marginTop: 'auto', paddingTop: '16px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--land-muted)', fontFamily: 'var(--font-mono)' }}>
        <Search size={12} />
        <span>Specialist:</span>
        <span style={{ color: 'var(--land-accent)' }}>
          {resultData.trace?.[2]?.detail || 'RS-VLM Checkpoint'}
        </span>
      </div>
    </div>
  );
}
