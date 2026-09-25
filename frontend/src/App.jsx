import React, { useState, useEffect } from 'react';
import LandingPage from './components/LandingPage';
import Header from './components/Header';
import IngestionPanel from './components/IngestionPanel';
import CanvasInspector from './components/CanvasInspector';
import ExecutiveSummary from './components/ExecutiveSummary';
import SuggestionChips from './components/SuggestionChips';
import FeedbackStrip from './components/FeedbackStrip';
import TelemetryDrawer from './components/TelemetryDrawer';
import ReportModal from './components/ReportModal';
import ProcessingView from './components/ProcessingView';
import { queryPipeline, logSuggestionClick } from './api/satquery';

export default function App() {
  // ── Theme state: 'dark' | 'light' ─────────────────────────────────
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('satquery_theme') || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.body.className = theme === 'light' ? 'light-theme' : '';
    localStorage.setItem('satquery_theme', theme);
  }, [theme]);

  // Prevent browser from navigating away if an image is dropped outside dropzone
  useEffect(() => {
    const preventDragDropNav = (e) => {
      e.preventDefault();
    };
    window.addEventListener('dragover', preventDragDropNav);
    window.addEventListener('drop', preventDragDropNav);
    return () => {
      window.removeEventListener('dragover', preventDragDropNav);
      window.removeEventListener('drop', preventDragDropNav);
    };
  }, []);

  const [isGrainFading, setIsGrainFading] = useState(false);

  const toggleTheme = () => {
    setIsGrainFading(true);
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
    setTimeout(() => {
      setIsGrainFading(false);
    }, 650);
  };

  // ── View state: 'landing' | 'workbench' ──────────────────────────
  const [view, setView] = useState('landing');

  // ── Workbench state (unchanged from original) ─────────────────────
  const [files, setFiles] = useState([]);
  const [rawImageUrls, setRawImageUrls] = useState([]);
  const [queryText, setQueryText] = useState('');
  const [activePreset, setActivePreset] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultData, setResultData] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);

  // Sync object URLs when files change
  useEffect(() => {
    const urls = files.map((f) => URL.createObjectURL(f));
    setRawImageUrls((prev) => {
      prev.forEach((u) => URL.revokeObjectURL(u));
      return urls;
    });
    return () => {
      urls.forEach((u) => URL.revokeObjectURL(u));
    };
  }, [files]);

  // ── Called from LandingPage ChatPanel submit ──────────────────────
  const handleLandingEnter = async ({ queryText: text, files: attachedFiles }) => {
    setQueryText(text);
    
    const validFiles = attachedFiles && attachedFiles.length > 0 ? attachedFiles : [];
    if (validFiles.length > 0) {
      setFiles(validFiles);
    } else {
      setErrorMessage("Please attach at least one satellite image to analyze.");
      return;
    }

    // Switch to processing state
    setView('processing');
    setErrorMessage(null);
    setIsProcessing(true);

    try {
      const data = await queryPipeline(validFiles, text);
      setResultData(data);
      setView('workbench');
    } catch (err) {
      console.error('Landing query execution error:', err);
      setErrorMessage(err.message || 'Analysis failed. Please check your image and try again.');
      setView('landing');
    } finally {
      setIsProcessing(false);
    }
  };

  // ── Return to landing ─────────────────────────────────────────────
  const handleBackToLanding = () => {
    setView('landing');
    setResultData(null);
    setErrorMessage(null);
    setActivePreset(null);
    // Keep query/files so user can continue if they navigate back
  };

  // ── Pipeline execution (unchanged from original) ──────────────────
  const executeQuery = async (queryToRun) => {
    const text = queryToRun || queryText;
    if (!text.trim() || files.length === 0 || isProcessing) return;

    setIsProcessing(true);
    setErrorMessage(null);
    try {
      const data = await queryPipeline(files, text);
      setResultData(data);
    } catch (err) {
      console.error('Query execution error:', err);
      setErrorMessage(err.message || 'Analysis failed. Check the pipeline trace for diagnostics.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSelectSuggestion = (suggestion) => {
    setQueryText(suggestion.text);
    if (resultData?.report_id) {
      logSuggestionClick({
        queryId: resultData.report_id,
        suggestionText: suggestion.text,
        taskType: suggestion.task_type,
      });
    }
    executeQuery(suggestion.text);
  };

  // ── Landing view ──────────────────────────────────────────────────
  if (view === 'landing') {
    return (
      <>
        {isGrainFading && (
          <div className={`theme-grain-shutter ${theme === 'light' ? 'to-light' : 'to-dark'}`} />
        )}
        <LandingPage
          onEnter={handleLandingEnter}
          errorMessage={errorMessage}
          theme={theme}
          onToggleTheme={toggleTheme}
        />
      </>
    );
  }

  // ── Processing view ───────────────────────────────────────────────
  if (view === 'processing') {
    return <ProcessingView />;
  }

  // ── Workbench view (original layout, unchanged) ───────────────────
  return (
    <>
      {isGrainFading && (
        <div className={`theme-grain-shutter ${theme === 'light' ? 'to-light' : 'to-dark'}`} />
      )}
      <div className="app-container">
        <Header
          hasResult={Boolean(resultData?.report_id)}
          onOpenReport={() => setIsReportModalOpen(true)}
          onBackToLanding={handleBackToLanding}
          theme={theme}
          onToggleTheme={toggleTheme}
        />

        <main className="command-center-layout">
          {/* Left Pane: Ingestion and Query */}
          <IngestionPanel
            files={files}
            setFiles={setFiles}
            rawImageUrls={rawImageUrls}
            queryText={queryText}
            setQueryText={setQueryText}
            isProcessing={isProcessing}
            onRunQuery={() => executeQuery(queryText)}
          />

          {/* Center Pane: Geospatial Canvas Inspector */}
          <CanvasInspector
            rawImageUrls={rawImageUrls}
            resultData={resultData}
            isProcessing={isProcessing}
          />

          {/* Right Pane: Summary, Suggestions, Telemetry */}
          <div className="panel right-panel">
            <ExecutiveSummary resultData={resultData} />

            {/* Inline error state */}
            {errorMessage && (
              <div className="error-inline">
                {errorMessage}
              </div>
            )}

            <SuggestionChips
              suggestions={resultData?.suggestions}
              onSelectSuggestion={handleSelectSuggestion}
              isProcessing={isProcessing}
            />

            <FeedbackStrip queryId={resultData?.report_id} />

            <TelemetryDrawer trace={resultData?.trace} />
          </div>
        </main>

        {isReportModalOpen && (
          <ReportModal
            reportId={resultData?.report_id}
            onClose={() => setIsReportModalOpen(false)}
          />
        )}
      </div>
    </>
  );
}
