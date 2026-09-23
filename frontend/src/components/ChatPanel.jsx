/**
 * ChatPanel — Glassmorphism AI chat panel for the SatQuery landing page.
 * Handles quick actions (populates input only), file attachment, and submit.
 * Submitting transitions the app to the analysis workbench.
 */

import React, { useState, useRef } from 'react';
import {
  Satellite,
  Paperclip,
  Mic,
  SendHorizonal,
  ScanEye,
  GitCompare,
  MapPin,
  Database,
  X,
  FileImage,
} from 'lucide-react';

const QUICK_ACTIONS = [
  {
    id: 'analyze',
    icon: ScanEye,
    label: 'Analyze a satellite image',
    prompt: 'Analyze this satellite image and identify key features, land cover types, and any notable structures or changes.',
  },
  {
    id: 'compare',
    icon: GitCompare,
    label: 'Compare two time periods',
    prompt: 'Compare these two satellite images from different time periods and detect any significant changes in the scene.',
  },
  {
    id: 'find',
    icon: MapPin,
    label: 'Find objects or regions',
    prompt: 'Identify and locate all objects, structures, or regions of interest in this satellite image.',
  },
  {
    id: 'explain',
    icon: Database,
    label: 'Explain a dataset',
    prompt: 'Explain what this satellite imagery dataset shows and provide an analysis of the observed patterns.',
  },
];

export default function ChatPanel({ onSubmit, errorMessage }) {
  const [query, setQuery] = useState('');
  const [files, setFiles] = useState([]);
  const [isFocused, setIsFocused] = useState(false);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const handleQuickAction = (action) => {
    setQuery(action.prompt);
    // Focus the input so user sees the text
    setTimeout(() => textareaRef.current?.focus(), 50);
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files);
      setFiles(prev => [...prev, ...selected].slice(0, 2));
    }
    // Reset input so same file can be re-added after removal
    e.target.value = '';
  };

  const handleRemoveFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    const trimmed = query.trim();
    if (!trimmed) return;
    // Pass query text and files up — App will switch to workbench
    onSubmit({ queryText: trimmed, files });
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const canSubmit = query.trim().length > 0;

  return (
    <aside className="chat-panel-glass" role="complementary" aria-label="SAT Query chat panel">

      {/* ── Brand header ─────────────────────────────────────── */}
      <div className="cp-brand">
        <div className="cp-brand-icon">
          <Satellite size={18} strokeWidth={1.8} />
        </div>
        <div className="cp-brand-text">
          <span className="cp-brand-name">SAT QUERY</span>
          <span className="cp-brand-tagline">Satellite Intelligence, Simplified.</span>
        </div>
      </div>

      {/* ── Greeting ─────────────────────────────────────────── */}
      <div className="cp-greeting">
        <h1 className="cp-greeting-hi">Hi there! 👋</h1>
        <p className="cp-greeting-sub">How can I help you today?</p>
        <p className="cp-greeting-desc">
          Ask anything about satellite data, earth observation, missions, or analysis.
        </p>
      </div>

      {/* ── Quick Actions ─────────────────────────────────────── */}
      <div className="cp-quick-actions">
        {QUICK_ACTIONS.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.id}
              className="cp-quick-btn"
              onClick={() => handleQuickAction(action)}
              type="button"
              aria-label={action.label}
            >
              <span className="cp-quick-icon">
                <Icon size={14} strokeWidth={1.8} />
              </span>
              <span className="cp-quick-label">{action.label}</span>
            </button>
          );
        })}
      </div>

      {/* ── Attached files ───────────────────────────────────── */}
      {files.length > 0 && (
        <div className="cp-files-list">
          {files.map((f, idx) => (
            <div key={idx} className="cp-file-pill">
              <FileImage size={12} className="cp-file-icon" />
              <span className="cp-file-name">{f.name}</span>
              <button
                type="button"
                className="cp-file-remove"
                onClick={() => handleRemoveFile(idx)}
                aria-label={`Remove ${f.name}`}
              >
                <X size={11} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* ── Chat input ───────────────────────────────────────── */}
      {errorMessage && (
        <div className="cp-error-message">
          {errorMessage}
        </div>
      )}
      <div className={`cp-input-container ${isFocused ? 'focused' : ''}`}>
        <textarea
          ref={textareaRef}
          className="cp-textarea"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Ask SAT Query anything..."
          rows={3}
          aria-label="Query input"
        />

        <div className="cp-input-actions">
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,.tif,.tiff"
            multiple
            style={{ display: 'none' }}
            onChange={handleFileChange}
            aria-hidden="true"
          />

          <div className="cp-input-left">
            <button
              type="button"
              className="cp-icon-btn"
              onClick={() => fileInputRef.current?.click()}
              title="Attach satellite image"
              aria-label="Attach image"
            >
              <Paperclip size={15} strokeWidth={1.8} />
            </button>
            <button
              type="button"
              className="cp-icon-btn"
              title="Voice input"
              aria-label="Voice input"
            >
              <Mic size={15} strokeWidth={1.8} />
            </button>
            <span className="cp-hint">Ctrl+Enter to send</span>
          </div>

          <button
            type="button"
            className={`cp-send-btn ${canSubmit ? 'active' : ''}`}
            onClick={handleSubmit}
            disabled={!canSubmit}
            aria-label="Send query"
          >
            <SendHorizonal size={15} strokeWidth={2} />
          </button>
        </div>
      </div>

      {/* ── Footer note ──────────────────────────────────────── */}
      <p className="cp-footer-note">
        Powered by multi-modal satellite intelligence · RS-VLM · JEV-JEPA
      </p>
    </aside>
  );
}
