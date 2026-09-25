/**
 * LandingPage — Full cinematic satellite intelligence landing experience.
 * Left: glassmorphism ChatPanel
 * Right: 3D EarthScene (Three.js)
 * Submitting the chat panel triggers onEnter() → App switches to workbench.
 */

import React from 'react';
import ChatPanel from './ChatPanel';
import EarthScene from './EarthScene';
import ThemeToggle from './ThemeToggle';

export default function LandingPage({ onEnter, errorMessage, theme = 'dark', onToggleTheme }) {
  const handleSubmit = ({ queryText, files }) => {
    onEnter({ queryText, files });
  };

  return (
    <div className="landing-layout">
      {/* Top Header Layer */}
      <header className="landing-header" aria-label="Landing Branding">
        {/* Left top slot: Theme Toggle */}
        <div className="lh-header-spacer" style={{ display: 'flex', alignItems: 'center', paddingLeft: '24px', pointerEvents: 'auto', zIndex: 100 }}>
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
        </div>

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
                <div className="lh-tagline-1">Self-Adapting Multi-Modal Satellite Intelligence</div>
                <div className="lh-tagline-2">Explore. Ask. Discover.</div>
              </div>
            </div>
            <ChatPanel onSubmit={handleSubmit} errorMessage={errorMessage} />
          </div>
        </div>

        {/* Right: 3D Earth Scene */}
        <div className="landing-right">
          <EarthScene isLightMode={theme === 'light'} />
        </div>
      </div>
    </div>
  );
}
