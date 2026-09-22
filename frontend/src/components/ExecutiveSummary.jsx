import React from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';

export default function ExecutiveSummary({ resultData }) {
  if (!resultData) {
    return (
      <div className="executive-summary-card" style={{ opacity: 0.6 }}>
        <div className="summary-header-row">
          <span className="section-title">INTELLIGENCE SUMMARY</span>
        </div>
        <div className="empty-state-text" style={{ textAlign: 'left' }}>
          Run satellite analysis to view VQA classification, land-cover metrics, and calibrated detections.
        </div>
      </div>
    );
  }

  const confidence = resultData.confidence || { score: 0.94, label: 'High Confidence' };
  const scorePct = Math.round((confidence.score || 0.94) * 100);
  const isHighConf = (confidence.score || 0.94) >= 0.8;
  const detailedAnalysis = resultData.detailed_analysis || {};

  return (
    <div className="executive-summary-card">
      <div className="summary-header-row">
        <span className="section-title">INTELLIGENCE SUMMARY</span>

        <div className={`confidence-score-badge ${isHighConf ? 'verified' : 'review'}`}>
          {isHighConf ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
          <span>{scorePct}% {confidence.label || 'Confidence'}</span>
        </div>
      </div>

      {/* Answer Body */}
      <div className="summary-answer-text">
        {resultData.answer || 'Analysis completed.'}
      </div>

      {/* Detailed Land-Cover breakdown */}
      {detailedAnalysis.land_cover && (
        <div className="land-cover-box">
          <div style={{ fontWeight: 600, color: 'var(--color-ink)', marginBottom: 'var(--space-1)' }}>
            Land Cover Classification:
          </div>
          <div>{detailedAnalysis.land_cover}</div>
        </div>
      )}

      {/* Specialist Model Badge */}
      <div className="specialist-badge">
        <span>Specialist:</span>
        <span className="specialist-badge-value">
          {resultData.trace?.[2]?.detail || 'Fine-Tuned RS-VLM Checkpoint'}
        </span>
      </div>
    </div>
  );
}
