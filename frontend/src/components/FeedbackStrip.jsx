import React, { useState } from 'react';
import { Check, Flag } from 'lucide-react';
import { submitOperatorFeedback } from '../api/satquery';

export default function FeedbackStrip({ queryId }) {
  const [submittedRating, setSubmittedRating] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFeedback = async (rating) => {
    if (!queryId || isSubmitting) return;
    setIsSubmitting(true);
    try {
      await submitOperatorFeedback({
        queryId,
        rating,
        notes: rating === 'accept' ? 'Operator accepted verification output' : 'Operator flagged detection discrepancy',
      });
      setSubmittedRating(rating);
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!queryId) return null;

  return (
    <div>
      <div className="section-header" style={{ marginBottom: 'var(--space-2)' }}>
        <span className="section-title">OPERATOR VERIFICATION</span>
        {submittedRating && (
          <span style={{ fontSize: '11px', color: 'var(--status-success)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
            LOGGED
          </span>
        )}
      </div>

      <div className="feedback-controls-bar">
        <button
          className={`feedback-action-btn accept ${submittedRating === 'accept' ? 'selected' : ''}`}
          onClick={() => handleFeedback('accept')}
          disabled={isSubmitting}
        >
          <Check size={13} />
          <span>Accept</span>
        </button>

        <button
          className={`feedback-action-btn flag ${submittedRating === 'flag_inaccurate' ? 'selected' : ''}`}
          onClick={() => handleFeedback('flag_inaccurate')}
          disabled={isSubmitting}
        >
          <Flag size={13} />
          <span>Flag Inaccurate</span>
        </button>
      </div>
    </div>
  );
}
