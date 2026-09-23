import React, { useState, useEffect } from 'react';
import { Check, Flag, Sliders, CheckCircle2 } from 'lucide-react';
import { submitOperatorFeedback } from '../api/satquery';

export default function FeedbackStrip({ queryId }) {
  const [submittedRating, setSubmittedRating] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedReason, setSelectedReason] = useState('');
  const [showDetails, setShowDetails] = useState(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState(false);

  // Reset feedback state whenever a new query result arrives
  useEffect(() => {
    setSubmittedRating(null);
    setSelectedReason('');
    setShowDetails(false);
    setFeedbackSuccess(false);
  }, [queryId]);

  const handleFeedback = async (rating, reasonOverride = '') => {
    if (!queryId || isSubmitting) return;
    setIsSubmitting(true);
    const reason = reasonOverride || selectedReason;
    const noteText = rating === 'accept'
      ? 'Operator accepted verification output'
      : (reason ? `Operator flagged: ${reason}` : 'Operator flagged detection discrepancy');

    try {
      await submitOperatorFeedback({
        queryId,
        rating,
        notes: noteText,
      });
      setSubmittedRating(rating);
      setFeedbackSuccess(true);
      setShowDetails(false);
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!queryId) return null;

  return (
    <div style={{ marginTop: 'var(--space-3)' }}>
      <div className="section-header" style={{ marginBottom: 'var(--space-2)' }}>
        <span className="section-title">HUMAN-IN-THE-LOOP SELF-ADAPTATION</span>
        {feedbackSuccess && (
          <span style={{ fontSize: '11px', color: 'var(--status-success)', fontFamily: 'var(--font-mono)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <CheckCircle2 size={12} />
            ADAPTATION PROFILE UPDATED
          </span>
        )}
      </div>

      <div className="feedback-controls-bar">
        <button
          className={`feedback-action-btn accept ${submittedRating === 'accept' ? 'selected' : ''}`}
          onClick={() => handleFeedback('accept')}
          disabled={isSubmitting}
          title="Confirm model detection and reinforce confidence"
        >
          <Check size={13} />
          <span>Accept Verification</span>
        </button>

        <button
          className={`feedback-action-btn flag ${submittedRating === 'flag_inaccurate' ? 'selected' : ''}`}
          onClick={() => {
            if (submittedRating !== 'flag_inaccurate') {
              setShowDetails(!showDetails);
            }
          }}
          disabled={isSubmitting}
          title="Flag discrepancy to trigger model active learning calibration"
        >
          <Flag size={13} />
          <span>Flag Discrepancy</span>
        </button>
      </div>

      {/* Expandable Discrepancy Reason Selector */}
      {showDetails && (
        <div style={{
          marginTop: 'var(--space-2)',
          padding: 'var(--space-2)',
          background: 'var(--surface-sunken)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '11px',
          fontFamily: 'var(--font-mono)'
        }}>
          <div style={{ color: 'var(--text-muted)', marginBottom: '6px' }}>Select discrepancy category to adapt model sensitivity:</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '8px' }}>
            {[
              'Object count mismatch',
              'Bounding box misaligned',
              'Spectral land cover error',
              'Missed target feature'
            ].map((reason) => (
              <button
                key={reason}
                onClick={() => setSelectedReason(reason)}
                style={{
                  padding: '3px 8px',
                  background: selectedReason === reason ? 'var(--status-danger-dim, rgba(239, 68, 68, 0.2))' : 'var(--surface-default)',
                  border: `1px solid ${selectedReason === reason ? 'var(--status-danger)' : 'var(--border-subtle)'}`,
                  color: selectedReason === reason ? 'var(--status-danger)' : 'var(--text-secondary)',
                  borderRadius: '3px',
                  cursor: 'pointer',
                  fontSize: '10px'
                }}
              >
                {reason}
              </button>
            ))}
          </div>
          <button
            onClick={() => handleFeedback('flag_inaccurate')}
            disabled={isSubmitting}
            style={{
              padding: '4px 12px',
              background: 'var(--status-danger)',
              color: '#fff',
              border: 'none',
              borderRadius: '3px',
              fontWeight: 600,
              fontSize: '11px',
              cursor: 'pointer'
            }}
          >
            Submit Feedback & Adapt Model
          </button>
        </div>
      )}
    </div>
  );
}
