import React, { useRef, useState, useEffect } from 'react';
import {
  UploadCloud,
  FileImage,
  X,
  Play,
  RotateCw,
  Plus,
  Mic,
  MicOff,
} from 'lucide-react';

export default function IngestionPanel({
  files,
  setFiles,
  rawImageUrls,
  queryText,
  setQueryText,
  isProcessing,
  onRunQuery,
}) {
  const fileInputRef = useRef(null);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  // Initialize Web Speech API
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
          setQueryText(transcript);
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
  }, [setQueryText]);

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

  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const dragCounter = useRef(0);

  const handleFileChange = (e) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...selected].slice(0, 2));
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
        setFiles((prev) => [...prev, ...dropped].slice(0, 2));
      }
    }
  };

  const handleRemoveFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      if (!isProcessing && files.length > 0 && queryText.trim()) {
        onRunQuery();
      }
    }
  };

  return (
    <div
      className={`panel ${isDraggingOver ? 'drag-active' : ''}`}
      style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}
      onDragOver={handleDragOver}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Hidden File Input for Adding Images */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple
        accept="image/*,.tif,.tiff"
        style={{ display: 'none' }}
      />

      {/* ── Section: Active Uploaded Imagery ── */}
      <div>
        <div className="section-header" style={{ marginBottom: '10px' }}>
          <span className="section-title">ACTIVE RASTER IMAGERY</span>
          <span style={{ fontSize: '11px', color: 'var(--color-muted)', fontFamily: 'var(--font-mono)' }}>
            {files.length} / 2 LOADED
          </span>
        </div>

        {/* Dragging Active Overlay Banner */}
        {isDraggingOver && (
          <div className="drag-overlay-banner" style={{ marginBottom: '10px' }}>
            <UploadCloud size={20} />
            <span>Drop image to add to workspace (T1 Baseline / T2 Monitoring)</span>
          </div>
        )}

        {files.length > 0 ? (
          <div className="uploaded-imagery-preview" style={{ marginBottom: '8px' }}>
            {files.map((f, idx) => (
              <div key={idx} className="uploaded-image-card">
                <div className="uploaded-card-thumb">
                  {rawImageUrls && rawImageUrls[idx] ? (
                    <img src={rawImageUrls[idx]} alt={f.name} />
                  ) : (
                    <FileImage size={22} style={{ color: 'var(--color-accent)' }} />
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
                    <span style={{ color: 'var(--color-accent)' }}>
                      {idx === 0 ? 'Baseline (T1)' : 'Monitoring (T2)'}
                    </span>
                    <span>·</span>
                    <span>10m GSD</span>
                  </span>
                </div>
                <button
                  type="button"
                  className="uploaded-card-remove"
                  onClick={() => handleRemoveFile(idx)}
                  title={`Remove ${f.name}`}
                  aria-label={`Remove ${f.name}`}
                >
                  <X size={14} />
                </button>
              </div>
            ))}

            {files.length < 2 && (
              <button
                type="button"
                className="uploaded-attach-prompt"
                style={{ marginTop: '4px', padding: '8px 12px', fontSize: '11px' }}
                onClick={() => fileInputRef.current?.click()}
              >
                <Plus size={14} style={{ color: 'var(--color-accent)' }} />
                <span>Drag & Drop or Click to add Second Image (T2)</span>
              </button>
            )}
          </div>
        ) : (
          <div
            className={`uploaded-attach-prompt ${isDraggingOver ? 'drag-active' : ''}`}
            onClick={() => fileInputRef.current?.click()}
          >
            <UploadCloud size={18} style={{ color: 'var(--color-accent)' }} />
            <span>Click or Drag & Drop satellite imagery here (Sentinel-2, JPG, PNG)</span>
          </div>
        )}
      </div>

      {/* ── Section: Geospatial Chat Query Box ── */}
      <div className="query-box" style={{ marginTop: 'auto' }}>
        <div className="section-header" style={{ marginBottom: '8px' }}>
          <span className="section-title">GEOSPATIAL CHAT QUERY</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              type="button"
              className={`cp-icon-btn ${isListening ? 'listening' : ''}`}
              onClick={toggleListening}
              title={isListening ? "Stop listening (Microphone recording active)" : "Speech-to-text voice input"}
              aria-label={isListening ? "Stop voice input" : "Voice input"}
              style={{ width: '26px', height: '26px' }}
            >
              {isListening ? <MicOff size={14} /> : <Mic size={14} />}
            </button>
            <span style={{ fontSize: '10px', color: 'var(--color-muted)', fontFamily: 'var(--font-mono)' }}>
              {isListening ? 'Listening...' : 'Ctrl + Enter'}
            </span>
          </div>
        </div>
        <textarea
          className="query-textarea"
          value={queryText}
          onChange={(e) => setQueryText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isListening ? "🎙️ Listening... speak your visual query now..." : "Ask a spatial question about the uploaded satellite imagery..."}
          rows={4}
          style={{ minHeight: '90px' }}
        />
        <button
          className="btn-workbench btn-primary"
          data-state={isProcessing ? 'loading' : undefined}
          onClick={onRunQuery}
          disabled={isProcessing || files.length === 0 || !queryText.trim()}
          style={{ padding: '12px 16px', width: '100%', marginTop: '10px' }}
        >
          {isProcessing ? (
            <>
              <RotateCw size={14} style={{ animation: 'spin 1s linear infinite' }} />
              <span>EXECUTING PIPELINE</span>
            </>
          ) : (
            <>
              <Play size={14} fill="currentColor" />
              <span style={{ fontWeight: 700, letterSpacing: '0.05em', fontFamily: 'var(--font-land-display)' }}>
                RUN ANALYSIS
              </span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
