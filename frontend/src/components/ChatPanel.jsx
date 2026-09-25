/**
 * ChatPanel — Glassmorphism AI chat panel for the SatQuery landing page.
 * Handles quick actions (populates input only), file attachment, and submit.
 * Submitting transitions the app to the analysis workbench.
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  Satellite,
  Paperclip,
  Mic,
  MicOff,
  SendHorizonal,
  UploadCloud,
  X,
  FileImage,
} from 'lucide-react';

export default function ChatPanel({ onSubmit, errorMessage }) {
  const [query, setQuery] = useState('');
  const [files, setFiles] = useState([]);
  const [fileUrls, setFileUrls] = useState([]);
  const [isFocused, setIsFocused] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const recognitionRef = useRef(null);

  // Initialize Web Speech API SpeechRecognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event) => {
        let transcript = '';
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        if (transcript) {
          setQuery(transcript);
        }
      };

      recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
    };
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition is not supported in this browser. Please use Google Chrome, Microsoft Edge, or Safari.");
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.error("Speech recognition start failed:", err);
        setIsListening(false);
      }
    }
  };

  // Maintain local object URLs for image preview thumbnails
  useEffect(() => {
    const urls = files.map((f) => URL.createObjectURL(f));
    setFileUrls((prev) => {
      prev.forEach((u) => URL.revokeObjectURL(u));
      return urls;
    });
    return () => {
      urls.forEach((u) => URL.revokeObjectURL(u));
    };
  }, [files]);

  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const dragCounter = useRef(0);

  const handleFileChange = (e) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files);
      setFiles(prev => [...prev, ...selected].slice(0, 2));
    }
    e.target.value = '';
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current += 1;
    if (e.dataTransfer && e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDraggingOver(true);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer) {
      e.dataTransfer.dropEffect = 'copy';
    }
    if (!isDraggingOver) {
      setIsDraggingOver(true);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current -= 1;
    if (dragCounter.current <= 0) {
      dragCounter.current = 0;
      setIsDraggingOver(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current = 0;
    setIsDraggingOver(false);
    if (e.dataTransfer && e.dataTransfer.files) {
      const dropped = Array.from(e.dataTransfer.files).filter(
        f => f.type.startsWith('image/') || f.name.endsWith('.tif') || f.name.endsWith('.tiff')
      );
      if (dropped.length > 0) {
        setFiles(prev => [...prev, ...dropped].slice(0, 2));
      }
    }
  };

  const handleRemoveFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    const trimmed = query.trim();
    if (!trimmed) return;
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
    <aside
      className={`chat-panel-glass ${isDraggingOver ? 'drag-active' : ''}`}
      role="complementary"
      aria-label="SAT Query chat panel"
      onDragOver={handleDragOver}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >

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
          Upload satellite imagery and ask anything about earth observation, infrastructure, or change analysis.
        </p>
      </div>

      {/* Drag & drop overlay indicator */}
      {isDraggingOver && (
        <div className="drag-overlay-banner">
          <UploadCloud size={24} />
          <span>Release to attach satellite imagery (T1 Baseline / T2 Monitoring)</span>
        </div>
      )}

      {/* ── Uploaded Imagery Preview (Shows what has been uploaded) ── */}
      {files.length > 0 ? (
        <div className="uploaded-imagery-preview">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2px' }}>
            <span style={{ fontSize: '11px', color: 'var(--color-muted)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
              UPLOADED IMAGERY ({files.length}/2)
            </span>
            {files.length < 2 && (
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                style={{ background: 'none', border: 'none', color: 'var(--color-accent)', fontSize: '11px', fontFamily: 'var(--font-mono)', cursor: 'pointer' }}
              >
                + Add Second Image (T2)
              </button>
            )}
          </div>
          {files.map((f, idx) => (
            <div key={idx} className="uploaded-image-card">
              <div className="uploaded-card-thumb">
                {fileUrls[idx] ? (
                  <img src={fileUrls[idx]} alt={f.name} />
                ) : (
                  <FileImage size={20} style={{ color: 'var(--color-accent)' }} />
                )}
                <span className="uploaded-card-badge">
                  {idx === 0 ? 'T1' : 'T2'}
                </span>
              </div>
              <div className="uploaded-card-details">
                <span className="uploaded-card-filename" title={f.name}>{f.name}</span>
                <span className="uploaded-card-meta">
                  <span>{(f.size / 1024).toFixed(0)} KB</span>
                  <span>·</span>
                  <span style={{ color: 'var(--color-accent)' }}>{idx === 0 ? 'Baseline' : 'Monitoring'}</span>
                </span>
              </div>
              <button
                type="button"
                className="uploaded-card-remove"
                onClick={() => handleRemoveFile(idx)}
                aria-label={`Remove ${f.name}`}
              >
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div
          className={`uploaded-attach-prompt ${isDraggingOver ? 'drag-active' : ''}`}
          onClick={() => fileInputRef.current?.click()}
        >
          <UploadCloud size={16} style={{ color: 'var(--color-accent)' }} />
          <span>Click or Drag & Drop satellite imagery here (Sentinel-2, JPG, PNG)</span>
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
          placeholder={isListening ? "🎙️ Listening... speak your query now..." : "Ask SAT Query anything..."}
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
              className={`cp-icon-btn ${isListening ? 'listening' : ''}`}
              onClick={toggleListening}
              title={isListening ? "Stop listening (Microphone recording active)" : "Speech-to-text voice input"}
              aria-label={isListening ? "Stop voice input" : "Start voice input"}
            >
              {isListening ? (
                <MicOff size={15} strokeWidth={2} />
              ) : (
                <Mic size={15} strokeWidth={1.8} />
              )}
            </button>
            <span className="cp-hint">{isListening ? 'Recording speech...' : 'Ctrl+Enter to send'}</span>
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

    </aside>
  );
}
