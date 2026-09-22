import React from 'react';
import { X, FileJson, FileCode, FileDown, FileText } from 'lucide-react';

export default function ReportModal({ reportId, onClose }) {
  if (!reportId) return null;

  const formats = [
    { label: 'PDF Document', ext: 'pdf', icon: FileDown },
    { label: 'Word Document', ext: 'docx', icon: FileText },
    { label: 'Markdown Report', ext: 'md', icon: FileCode },
    { label: 'Raw JSON Payload', ext: 'json', icon: FileJson },
  ];

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-panel"
        style={{ position: 'relative' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div className="modal-title">Export Intelligence Report</div>
            <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontFamily: 'var(--font-mono)', fontVariantNumeric: 'tabular-nums', marginTop: 'var(--space-1)' }}>
              REPORT ID: {reportId}
            </div>
          </div>
          <button onClick={onClose} className="modal-close-btn" style={{ position: 'static' }}>
            <X size={16} />
          </button>
        </div>

        <div className="format-btn-grid">
          {formats.map((f) => {
            const Icon = f.icon;
            const downloadUrl = `/report/${reportId}?format=${f.ext}`;
            return (
              <a
                key={f.ext}
                href={downloadUrl}
                download
                target="_blank"
                rel="noreferrer"
                className="btn-workbench"
                style={{
                  textDecoration: 'none',
                  padding: 'var(--space-3) var(--space-4)',
                  justifyContent: 'flex-start',
                }}
              >
                <Icon size={15} />
                <span style={{ flex: 1 }}>{f.label}</span>
                <span style={{ fontSize: '10px', color: 'var(--color-muted)', fontFamily: 'var(--font-mono)' }}>
                  .{f.ext.toUpperCase()}
                </span>
              </a>
            );
          })}
        </div>
      </div>
    </div>
  );
}
