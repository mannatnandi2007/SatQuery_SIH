/**
 * SatQuery AI — Frontend Application Logic
 * Handles file upload, API calls, results rendering, and UI state management.
 */

// ── Configuration ──────────────────────────────────────
const API_BASE = (window.location && window.location.origin && window.location.origin.startsWith("http")) 
    ? window.location.origin 
    : "http://localhost:8000";

// ── State ──────────────────────────────────────────────
let uploadedFiles = [];
let currentReportUrl = null;

// ── Theme Switcher ──────────────────────────────────────
const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");
const themeLabel = document.getElementById("themeLabel");

function initTheme() {
    const savedTheme = localStorage.getItem("satquery_theme") || "light";
    applyTheme(savedTheme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("satquery_theme", theme);
    if (themeIcon && themeLabel) {
        if (theme === "dark") {
            themeIcon.textContent = "☀️";
            themeLabel.textContent = "Light";
        } else {
            themeIcon.textContent = "🌙";
            themeLabel.textContent = "Dark";
        }
    }
}

if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") || "light";
        applyTheme(current === "dark" ? "light" : "dark");
    });
}

initTheme();

// ── DOM Elements ───────────────────────────────────────
const uploadZone = document.getElementById("uploadZone");
const fileInput = document.getElementById("fileInput");
const fileChips = document.getElementById("fileChips");
const queryInput = document.getElementById("queryInput");
const submitBtn = document.getElementById("submitBtn");
const errorDisplay = document.getElementById("errorDisplay");
const errorText = document.getElementById("errorText");
const emptyState = document.getElementById("emptyState");
const loadingState = document.getElementById("loadingState");
const resultsContainer = document.getElementById("resultsContainer");

// ── Upload Zone Event Handlers ─────────────────────────

uploadZone.addEventListener("click", () => fileInput.click());

uploadZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadZone.classList.add("drag-over");
});

uploadZone.addEventListener("dragleave", (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadZone.classList.remove("drag-over");
});

uploadZone.addEventListener("drop", (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadZone.classList.remove("drag-over");

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
});

fileInput.addEventListener("change", (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
});

queryInput.addEventListener("input", () => {
    updateSubmitState();
    triggerLiveCompatibilityCheck();
});

// ── File Handling ──────────────────────────────────────

function handleFiles(files) {
    // Limit to 2 files max
    const validFiles = files.filter((f) => {
        const ext = f.name.toLowerCase().split(".").pop();
        return ["tif", "tiff", "jpg", "jpeg", "png"].includes(ext);
    });

    if (validFiles.length === 0) {
        showError("Please upload a valid satellite image (GeoTIFF, JPEG, or PNG).");
        return;
    }

    // Replace or append (max 2)
    uploadedFiles = [...uploadedFiles, ...validFiles].slice(0, 2);

    renderFileChips();
    updateUploadZoneState();
    updateSubmitState();
    hideError();
    triggerLiveCompatibilityCheck();
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    renderFileChips();
    updateUploadZoneState();
    updateSubmitState();
    triggerLiveCompatibilityCheck();
}

function renderFileChips() {
    fileChips.innerHTML = uploadedFiles
        .map(
            (file, i) => `
        <div class="file-chip">
            📄 ${file.name} (${formatFileSize(file.size)})
            <span class="remove-file" onclick="removeFile(${i})">✕</span>
        </div>
    `
        )
        .join("");
}

function updateUploadZoneState() {
    if (uploadedFiles.length > 0) {
        uploadZone.classList.add("has-files");
    } else {
        uploadZone.classList.remove("has-files");
    }
}

function updateSubmitState() {
    const hasFiles = uploadedFiles.length > 0;
    const hasQuery = queryInput.value.trim().length > 0;
    submitBtn.disabled = !(hasFiles && hasQuery);
}

function formatFileSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ── Demo Samples & Queries ─────────────────────────────

async function loadSample(sampleKey, defaultQuery) {
    const sampleMap = {
        urban_port: { path: "/samples/urban_port.jpg", name: "sat_urban_port.jpg" },
        farm_river: { path: "/samples/farm_river.jpg", name: "sat_farm_river.jpg" },
        airport_runway: { path: "/samples/airport_runway.jpg", name: "sat_airport_runway.jpg" }
    };

    const target = sampleMap[sampleKey];
    if (!target) return;

    try {
        const res = await fetch(target.path);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const blob = await res.blob();
        const file = new File([blob], target.name, { type: "image/jpeg" });

        uploadedFiles = [file];
        renderFileChips();
        updateUploadZoneState();

        if (defaultQuery) {
            queryInput.value = defaultQuery;
        }

        updateSubmitState();
        triggerLiveCompatibilityCheck();
    } catch (e) {
        console.error("Failed to load sample image:", e);
        showError("Could not load sample image from server.");
    }
}

function setDemoQuery(query) {
    queryInput.value = query;
    updateSubmitState();
    queryInput.focus();
    triggerLiveCompatibilityCheck();
}

// ── Live Compatibility Checking ────────────────────────

let liveCheckTimeout = null;

function triggerLiveCompatibilityCheck() {
    clearTimeout(liveCheckTimeout);
    const hasFiles = uploadedFiles.length > 0;
    const query = queryInput.value.trim();

    if (!hasFiles || !query) {
        hideError();
        return;
    }

    liveCheckTimeout = setTimeout(async () => {
        try {
            const formData = new FormData();
            uploadedFiles.forEach((file) => formData.append("images", file));
            formData.append("query", query);

            const res = await fetch(`${API_BASE}/compatibility-check`, {
                method: "POST",
                body: formData
            });

            if (res.ok) {
                const data = await res.json();
                if (!data.valid) {
                    showError(data.reason);
                    submitBtn.disabled = true;
                } else {
                    hideError();
                    submitBtn.disabled = false;
                }
            }
        } catch (e) {
            // Silently ignore if offline
        }
    }, 250);
}

// ── Error Handling ─────────────────────────────────────

function showError(message) {
    errorText.textContent = message;
    errorDisplay.classList.add("visible");
}

function hideError() {
    errorDisplay.classList.remove("visible");
}

// ── UI State Management ────────────────────────────────

function showEmpty() {
    emptyState.style.display = "block";
    loadingState.classList.remove("visible");
    resultsContainer.classList.remove("visible");
}

function showLoading() {
    emptyState.style.display = "none";
    loadingState.classList.add("visible");
    resultsContainer.classList.remove("visible");
    hideError();

    // Reset all stages
    document.querySelectorAll(".loading-stage").forEach((el) => {
        el.classList.remove("active", "completed");
    });
}

function showResults() {
    emptyState.style.display = "none";
    loadingState.classList.remove("visible");
    resultsContainer.classList.add("visible");
}

// ── Loading Stage Animation ────────────────────────────

const STAGE_IDS = [
    "stage-compatibility",
    "stage-routing",
    "stage-analyzing",
    "stage-evidence",
    "stage-report",
];

function advanceStage(stageIndex) {
    // Complete previous stages
    for (let i = 0; i < stageIndex; i++) {
        const el = document.getElementById(STAGE_IDS[i]);
        el.classList.remove("active");
        el.classList.add("completed");
        el.querySelector(".stage-indicator").textContent = "✓";
    }

    // Activate current stage
    if (stageIndex < STAGE_IDS.length) {
        const el = document.getElementById(STAGE_IDS[stageIndex]);
        el.classList.add("active");
    }
}

function completeAllStages() {
    STAGE_IDS.forEach((id) => {
        const el = document.getElementById(id);
        el.classList.remove("active");
        el.classList.add("completed");
        el.querySelector(".stage-indicator").textContent = "✓";
    });
}

// ── Submit & API Call ──────────────────────────────────

submitBtn.addEventListener("click", handleSubmit);

// Also submit on Ctrl+Enter in the query input
queryInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        handleSubmit();
    }
});

async function handleSubmit() {
    if (submitBtn.disabled) return;

    const query = queryInput.value.trim();
    if (!query || uploadedFiles.length === 0) return;

    // Disable submit, show loading
    submitBtn.disabled = true;
    submitBtn.textContent = "Processing...";
    showLoading();

    try {
        // Animate through stages with delays for visual effect
        advanceStage(0); // Compatibility Check

        // Build form data
        const formData = new FormData();
        uploadedFiles.forEach((file) => formData.append("images", file));
        formData.append("query", query);

        // Stage 1 → 2 transition
        await sleep(400);
        advanceStage(1); // Routing

        // Stage 2 → 3 transition
        await sleep(300);
        advanceStage(2); // Analyzing

        // Make the actual API call
        const response = await fetch(`${API_BASE}/query`, {
            method: "POST",
            body: formData,
        });

        // Stage 3 → 4 transition
        advanceStage(3); // Building Evidence
        await sleep(300);

        // Stage 4 → 5 transition
        advanceStage(4); // Generating Report
        await sleep(200);

        const data = await response.json();

        if (!response.ok || data.error) {
            completeAllStages();
            await sleep(300);
            showError(data.answer || "An unknown error occurred.");
            showEmpty();
            return;
        }

        // Complete all stages
        completeAllStages();
        await sleep(400);

        // Render results
        renderResults(data);
    } catch (err) {
        console.error("API Error:", err);
        showError(
            "Could not connect to the SatQuery AI backend. Make sure the server is running on http://localhost:8000"
        );
        showEmpty();
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Analyze Satellite Scene";
        updateSubmitState();
    }
}

// ── Render Results ─────────────────────────────────────

function renderResults(data) {
    // Answer
    document.getElementById("answerText").textContent = data.answer;

    // Confidence
    const badge = document.getElementById("confidenceBadge");
    const label = data.confidence.label.toLowerCase();
    badge.className = `confidence-badge ${label}`;
    document.getElementById("confidenceLabel").textContent =
        `${data.confidence.label} Confidence`;
    document.getElementById("confidenceScore").textContent =
        data.confidence.score.toFixed(3);

    // Evidence image
    const evidenceImg = document.getElementById("evidenceImage");
    const evidenceBadge = document.getElementById("evidenceTypeBadge");

    if (data.evidence && data.evidence.overlay_image_base64) {
        evidenceImg.src = `data:image/png;base64,${data.evidence.overlay_image_base64}`;
        evidenceBadge.textContent =
            data.evidence.type === "bbox" ? "BOUNDING BOX" : data.evidence.type.toUpperCase();
    } else if (data.evidence && data.evidence.overlay_image_url) {
        evidenceImg.src = `${API_BASE}${data.evidence.overlay_image_url}`;
        evidenceBadge.textContent = data.evidence.type.toUpperCase();
    }

    // Execution Trace
    renderTrace(data.trace);

    // Report URL
    currentReportUrl = data.report_url;
    const downloadBtn = document.getElementById("downloadBtn");
    if (data.report_url) {
        downloadBtn.style.display = "inline-flex";
    } else {
        downloadBtn.style.display = "none";
    }

    showResults();
}

// ── Execution Trace ────────────────────────────────────

function renderTrace(trace) {
    const traceList = document.getElementById("traceList");
    const totalMs = trace.reduce((sum, t) => sum + (t.duration_ms || 0), 0);

    document.getElementById("traceDuration").textContent = `${totalMs}ms total`;

    traceList.innerHTML = trace
        .map(
            (entry) => `
        <div class="trace-item">
            <div class="trace-status ${entry.status}"></div>
            <span class="trace-stage">${entry.stage}</span>
            <span class="trace-detail" title="${escapeHtml(entry.detail)}">${escapeHtml(entry.detail)}</span>
            <span class="trace-duration">${entry.duration_ms}ms</span>
        </div>
    `
        )
        .join("");
}

function toggleTrace() {
    const toggle = document.getElementById("traceToggle");
    const list = document.getElementById("traceList");

    toggle.classList.toggle("expanded");
    list.classList.toggle("visible");
}

// ── Report Download ────────────────────────────────────

function downloadReport() {
    if (currentReportUrl) {
        window.open(`${API_BASE}${currentReportUrl}`, "_blank");
    }
}

// ── Utilities ──────────────────────────────────────────

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// ── Initialize ─────────────────────────────────────────
showEmpty();
console.log(
    "%c🛰️ SatQuery AI Frontend Loaded",
    "color: #00d4ff; font-size: 14px; font-weight: bold;"
);
