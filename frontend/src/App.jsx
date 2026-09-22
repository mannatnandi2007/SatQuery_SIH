import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import IngestionPanel from './components/IngestionPanel';
import CanvasInspector from './components/CanvasInspector';
import ExecutiveSummary from './components/ExecutiveSummary';
import SuggestionChips from './components/SuggestionChips';
import FeedbackStrip from './components/FeedbackStrip';
import TelemetryDrawer from './components/TelemetryDrawer';
import ReportModal from './components/ReportModal';
import { queryPipeline, logSuggestionClick } from './api/satquery';

export default function App() {
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

  return (
    <div className="app-container">
      <Header
        hasResult={Boolean(resultData?.report_id)}
        onOpenReport={() => setIsReportModalOpen(true)}
      />

      <main className="command-center-layout">
        {/* Left Pane: Ingestion and Query */}
        <IngestionPanel
          files={files}
          setFiles={setFiles}
          queryText={queryText}
          setQueryText={setQueryText}
          isProcessing={isProcessing}
          onRunQuery={() => executeQuery(queryText)}
          activePreset={activePreset}
          setActivePreset={setActivePreset}
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

          {/* Inline error state instead of alert() */}
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
  );
}
