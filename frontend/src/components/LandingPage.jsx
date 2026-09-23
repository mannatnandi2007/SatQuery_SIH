/**
 * LandingPage — Full cinematic satellite intelligence landing experience.
 * Left: glassmorphism ChatPanel
 * Right: 3D EarthScene (Three.js)
 * Submitting the chat panel triggers onEnter() → App switches to workbench.
 */

import React from 'react';
import ChatPanel from './ChatPanel';
import EarthScene from './EarthScene';

export default function LandingPage({ onEnter, errorMessage }) {
  const handleSubmit = ({ queryText, files }) => {
    onEnter({ queryText, files });
  };

  return (
    <div className="landing-layout">
      {/* Top Header Layer */}
      <header className="landing-header" aria-label="Landing Branding">
        {/* The left branding has been moved down to the chat panel wrapper */}
        <div className="lh-header-spacer" />

        <div className="lh-right-tagline">
          <div>FROM</div>
          <div>SPACE</div>
          <div className="lh-right-sub">TO A BRIGHTER</div>
          <div className="lh-right-sub">TOMORROW</div>
          <div className="lh-right-accent" />
        </div>
      </header>

      {/* Main Content Area */}
      <div className="landing-main">
        {/* Left: Chat Panel & Branding */}
        <div className="landing-left">
          <div className="landing-left-content">
            <div className="lh-brand">
              <div className="lh-logo-text">
                <span className="lh-logo-sat">SAT</span> <span className="lh-logo-query">QUERY</span>
              </div>
              <div className="lh-taglines">
                <div className="lh-tagline-1">Satellite Intelligence, Simplified.</div>
                <div className="lh-tagline-2">Explore. Ask. Discover.</div>
              </div>
            </div>
            <ChatPanel onSubmit={handleSubmit} errorMessage={errorMessage} />
          </div>
        </div>

        {/* Right: 3D Earth Scene */}
        <div className="landing-right">
          <EarthScene />

          {/* Floating label below Earth */}
          <div className="landing-earth-label" aria-hidden="true">
            <span className="landing-earth-label-dot" />
            <span>Live orbital tracking · 4 assets</span>
          </div>
        </div>
      </div>
    </div>
  );
}
