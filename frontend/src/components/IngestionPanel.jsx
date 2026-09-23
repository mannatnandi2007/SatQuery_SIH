import React, { useRef } from 'react';
import {
  UploadCloud,
  FileImage,
  X,
  Play,
  RotateCw,
  Plane,
  GitCompare,
  Radio,
  Sprout,
  Anchor,
  Building2,
} from 'lucide-react';

const PRESETS = [
  {
    id: 'building_count',
    label: 'Industrial Building Count (T1)',
    icon: Building2,
    query: 'Count how many buildings are located in this industrial complex and highlight each structure.',
    files: ['/samples/urban_port.jpg'],
  },
  {
    id: 'runway',
    label: 'Aerodrome Runway Inspection',
    icon: Plane,
    query: 'Count all aircraft parked along the terminal apron and verify runway spatial clearance.',
    files: ['/samples/airport_runway.jpg'],
  },
  {
    id: 'change',
    label: 'Bi-Temporal Port Change (T1/T2)',
    icon: GitCompare,
    query: 'Perform bi-temporal change detection and identify any new logistics warehouse construction or altered waterfront infrastructure.',
    files: ['/samples/port_t1.jpg', '/samples/port_t2.jpg'],
  },
  {
    id: 'sar',
    label: 'Optical + SAR Fusion',
    icon: Radio,
    query: 'Execute co-registered Sentinel-1 SAR and optical fusion to detect metallic vessel signatures in the shipping lane.',
    files: ['/samples/urban_port.jpg', '/samples/port_sar.jpg'],
  },
  {
    id: 'farm',
    label: 'Farmland and Hydrology',
    icon: Sprout,
    query: 'Examine crop parcel phenology and identify active irrigation drainage networks.',
    files: ['/samples/farm_river.jpg'],
  },
  {
    id: 'harbor',
    label: 'Urban Harbor Grounding',
    icon: Anchor,
    query: 'Identify and localize all maritime transport vessels and cargo loading piers.',
    files: ['/samples/urban_port.jpg'],
  },
];

export default function IngestionPanel({
  files,
  setFiles,
  queryText,
  setQueryText,
  isProcessing,
  onRunQuery,
  activePreset,
  setActivePreset,
}) {
  const fileInputRef = useRef(null);

  const handleSelectPreset = async (preset) => {
    setActivePreset(preset.id);
    setQueryText(preset.query);

    try {
      const loadedFiles = [];
      for (const url of preset.files) {
        const res = await fetch(url);
        const blob = await res.blob();
        const filename = url.split('/').pop();
        loadedFiles.push(new File([blob], filename, { type: blob.type || 'image/jpeg' }));
      }
      setFiles(loadedFiles);
    } catch (err) {
      console.error('Failed to load preset files:', err);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...selected].slice(0, 2));
      setActivePreset(null);
    }
  };

  const handleRemoveFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
    setActivePreset(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      if (!isProcessing && files.length > 0) {
        onRunQuery();
      }
    }
  };

  return (
    <div className="panel">
      {/* Benchmark Presets */}
      <div>
        <div className="section-header">
          <span className="section-title">BENCHMARK SCENES</span>
        </div>
        <div className="presets-grid" style={{ marginTop: '8px' }}>
          {PRESETS.map((p) => {
            const Icon = p.icon;
            const isActive = activePreset === p.id;
            return (
              <button
                key={p.id}
                onClick={() => handleSelectPreset(p)}
                className={`preset-chip ${isActive ? 'active' : ''}`}
              >
                <Icon size={14} />
                <span>{p.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Raster Upload Dropzone */}
      <div>
        <div className="section-header">
          <span className="section-title">RASTER IMAGERY</span>
          <span style={{ fontSize: '11px', color: 'var(--color-muted)', fontFamily: 'var(--font-mono)', fontVariantNumeric: 'tabular-nums' }}>
            {files.length} / 2
          </span>
        </div>

        <div
          className="dropzone-area"
          style={{ marginTop: '8px' }}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            multiple
            accept="image/*,.tif,.tiff"
            style={{ display: 'none' }}
          />
          <div className="dropzone-icon-circle" style={{ background: 'transparent', border: 'none' }}>
            <UploadCloud size={20} style={{ color: 'var(--color-muted)' }} />
          </div>
          <div>
            <div style={{ fontWeight: 500, color: 'var(--color-ink-2)', fontSize: '13px' }}>
              Drop raster files or click to browse
            </div>
            <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '4px' }}>
              GeoTIFF, PNG, JPG. Supports multi-temporal pairs (T1/T2).
            </div>
          </div>
        </div>

        {files.length > 0 && (
          <div className="uploaded-files-list">
            {files.map((f, idx) => (
              <div key={idx} className="file-item-pill" style={{ background: 'rgba(80, 140, 255, 0.08)', border: '1px solid rgba(80, 140, 255, 0.3)', color: '#fff' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FileImage size={12} style={{ color: 'var(--color-accent)' }} />
                  {f.name} <span style={{ color: 'var(--color-muted)' }}>({(f.size / 1024).toFixed(0)} KB)</span>
                </span>
                <button
                  type="button"
                  onClick={() => handleRemoveFile(idx)}
                  className="file-remove-btn"
                >
                  <X size={13} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Query Input Box */}
      <div className="query-box">
        <div className="section-header">
          <span className="section-title">VISUAL QUERY</span>
          <span style={{ fontSize: '10px', color: 'var(--color-muted)', fontFamily: 'var(--font-mono)' }}>
            Ctrl + Enter
          </span>
        </div>
        <textarea
          className="query-textarea"
          value={queryText}
          onChange={(e) => setQueryText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a spatial question about the uploaded scene..."
        />
        <button
          className={`btn-workbench btn-primary ${isProcessing ? '' : ''}`}
          data-state={isProcessing ? 'loading' : undefined}
          onClick={onRunQuery}
          disabled={isProcessing || files.length === 0 || !queryText.trim()}
          style={{ padding: '12px 16px' }}
        >
          {isProcessing ? (
            <>
              <RotateCw size={14} className="processing-spinner" style={{ border: 'none', width: 'auto', height: 'auto', animation: 'spin 1s linear infinite' }} />
              <span>EXECUTING PIPELINE</span>
            </>
          ) : (
            <>
              <Play size={14} fill="currentColor" />
              <span style={{ fontWeight: 700, letterSpacing: '0.05em', fontFamily: 'var(--font-land-display)' }}>RUN ANALYSIS</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
