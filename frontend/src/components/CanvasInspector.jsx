import React, { useState, useRef } from 'react';
import { Eye, Split, Image as ImageIcon } from 'lucide-react';

export default function CanvasInspector({
  rawImageUrls,
  resultData,
  isProcessing,
}) {
  const [viewMode, setViewMode] = useState('evidence');
  const [reticleCoords, setReticleCoords] = useState({ x: null, y: null });
  const containerRef = useRef(null);

  const overlayBase64 = resultData?.evidence?.overlay_image_base64;
  const overlayUrl = resultData?.evidence?.overlay_image_url;
  const evidenceSrc = overlayBase64
    ? `data:image/png;base64,${overlayBase64}`
    : overlayUrl || rawImageUrls[0];

  const rawSrc = rawImageUrls[0] || null;
  const rawSecondSrc = rawImageUrls[1] || null;

  const annotationSet = resultData?.annotation_set || [];

  const handleMouseMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.round(e.clientX - rect.left);
    const y = Math.round(e.clientY - rect.top);
    setReticleCoords({ x: Math.max(0, x), y: Math.max(0, y) });
  };

  const handleMouseLeave = () => {
    setReticleCoords({ x: null, y: null });
  };

  const groundDistanceX = reticleCoords.x !== null ? (reticleCoords.x * 10.0).toFixed(0) : '--';
  const groundDistanceY = reticleCoords.y !== null ? (reticleCoords.y * 10.0).toFixed(0) : '--';

  return (
    <div className="panel center-panel">
      {/* Canvas Viewport Toolbar */}
      <div className="canvas-header-bar">
        <span className="canvas-header-label">
          GEOSPATIAL INSPECTOR
        </span>

        <div className="view-mode-tabs">
          <button
            className={`mode-tab-btn ${viewMode === 'evidence' ? 'active' : ''}`}
            onClick={() => setViewMode('evidence')}
          >
            <Eye size={11} />
            Evidence
          </button>
          <button
            className={`mode-tab-btn ${viewMode === 'raw' ? 'active' : ''}`}
            onClick={() => setViewMode('raw')}
          >
            <ImageIcon size={11} />
            Raw
          </button>
          <button
            className={`mode-tab-btn ${viewMode === 'dual' ? 'active' : ''}`}
            onClick={() => setViewMode('dual')}
          >
            <Split size={11} />
            Dual
          </button>
        </div>
      </div>

      {/* Visual Canvas Viewport */}
      <div
        className="canvas-viewport-container"
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        {isProcessing && (
          <div className="processing-overlay">
            <div className="processing-spinner" />
            <span className="processing-label">
              FUSING SPECIALIST DETECTIONS
            </span>
          </div>
        )}

        {/* Dual View Mode */}
        {viewMode === 'dual' ? (
          <div className="dual-view-grid">
            <div className="dual-raster-panel">
              <span className="raster-badge-tag">RAW INPUT (GSD 10m)</span>
              {rawSrc ? (
                <img src={rawSrc} alt="Raw Scene T1" className="main-raster-img" />
              ) : (
                <span className="empty-state-text">Load raster imagery</span>
              )}
            </div>
            <div className="dual-raster-panel">
              <span className="raster-badge-tag">
                {rawSecondSrc && !resultData ? 'MONITORING INPUT T2' : 'EVIDENCE OVERLAY'}
              </span>
              {evidenceSrc || rawSecondSrc ? (
                <img
                  src={evidenceSrc || rawSecondSrc}
                  alt="Evidence Overlay"
                  className="main-raster-img"
                />
              ) : (
                <span className="empty-state-text">Run query to inspect</span>
              )}
            </div>
          </div>
        ) : viewMode === 'raw' ? (
          rawSrc ? (
            <img src={rawSrc} alt="Raw Scene" className="main-raster-img" />
          ) : (
            <div className="empty-state-text">
              Select a benchmark preset or upload imagery to begin
            </div>
          )
        ) : (
          evidenceSrc ? (
            <img src={evidenceSrc} alt="Evidence Grounding Overlay" className="main-raster-img" />
          ) : (
            <div className="empty-state-text">
              Run satellite analysis to generate visual grounding
            </div>
          )
        )}
      </div>

      {/* Layer Legend Strip and HUD Telemetry */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {annotationSet.length > 0 && (
          <div className="legend-strip-container">
            <span style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
              LAYERS:
            </span>
            {annotationSet.map((layer, idx) => (
              <div key={idx} className="legend-tag-pill">
                <span
                  className="legend-circle-marker"
                  style={{ backgroundColor: layer.color || 'var(--color-accent)' }}
                />
                <span style={{ textTransform: 'capitalize', color: 'var(--color-ink)' }}>
                  {layer.reasoning}: {layer.boxes?.length || 0}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Reticle HUD Strip */}
        <div className="canvas-hud-strip">
          <div className="hud-item">
            <span>COORD:</span>
            <span className="hud-val">
              {reticleCoords.x !== null ? `${reticleCoords.x} px, ${reticleCoords.y} px` : '-- px, -- px'}
            </span>
          </div>
          <div className="hud-item">
            <span>GROUND:</span>
            <span className="hud-val">
              ~{groundDistanceX} m, ~{groundDistanceY} m
            </span>
          </div>
          <div className="hud-item">
            <span>CALIBRATION:</span>
            <span className="hud-val" style={{ color: 'var(--color-accent)' }}>
              10.0 m/px
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
