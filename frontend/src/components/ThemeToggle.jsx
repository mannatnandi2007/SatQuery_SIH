import React from 'react';
import { Sun, Moon } from 'lucide-react';

/**
 * ThemeToggle — Interactive celestial theme switch with sun rising/setting animation.
 * Features an animated celestial viewport where the sun rises up into the sky on light mode,
 * and sets downward below the horizon on dark mode while the moon rises.
 */
export default function ThemeToggle({ theme, onToggle }) {
  const isLight = theme === 'light';

  const handleClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (typeof onToggle === 'function') {
      onToggle();
    }
  };

  return (
    <div className="theme-toggle-wrapper" title={`Switch to ${isLight ? 'Dark Space' : 'Light Aerospace'} Mode`}>
      <button
        type="button"
        className={`theme-toggle-btn ${isLight ? 'is-light' : 'is-dark'}`}
        onClick={handleClick}
        aria-label={`Toggle theme (currently ${theme})`}
      >
        {/* Celestial Stage with Animated Sun / Moon Horizon */}
        <div className="celestial-stage">
          {/* Sun: Rises up from below horizon in light mode, sets down in dark mode */}
          <div className={`celestial-body sun-orb ${isLight ? 'sun-risen' : 'sun-set'}`}>
            <Sun size={15} strokeWidth={2.4} />
            <div className="sun-corona" />
          </div>

          {/* Moon: Rises up in dark mode, sinks down in light mode */}
          <div className={`celestial-body moon-orb ${isLight ? 'moon-set' : 'moon-risen'}`}>
            <Moon size={14} strokeWidth={2.2} />
            <div className="moon-glow" />
          </div>
        </div>

        {/* Toggle label */}
        <span className="theme-toggle-label">
          {isLight ? 'DAY' : 'NIGHT'}
        </span>
      </button>
    </div>
  );
}
