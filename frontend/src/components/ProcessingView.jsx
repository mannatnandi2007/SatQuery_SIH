import React, { useState, useEffect } from 'react';
import { Satellite } from 'lucide-react';

const STATUS_MESSAGES = [
  'Routing query...',
  'Inspecting imagery...',
  'Running satellite analysis...',
  'Generating evidence...',
  'Synthesizing insights...',
];

export default function ProcessingView() {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    // Cycle through status messages every 2.5 seconds, but stop at the last one
    // so it doesn't loop back to "Routing query" if the API takes a long time.
    const interval = setInterval(() => {
      setMessageIndex((prev) => Math.min(prev + 1, STATUS_MESSAGES.length - 1));
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="processing-view-container">
      {/* Background ambient glow matching the AI mesh concept */}
      <div className="processing-bg-glow"></div>
      
      <div className="processing-content">
        <div className="processing-brand">
          <Satellite size={48} className="processing-icon" />
          <div className="processing-logo-text">
            <span className="lh-logo-sat">SAT</span> <span className="lh-logo-query">QUERY</span>
          </div>
        </div>

        <div className="processing-status-primary">
          Analyzing satellite data...
        </div>

        <div className="processing-status-secondary">
          {STATUS_MESSAGES[messageIndex]}
        </div>

        {/* Loading Indicator (Scanning line or pulsing bar) */}
        <div className="processing-loader">
          <div className="processing-loader-bar"></div>
        </div>
      </div>
    </div>
  );
}
