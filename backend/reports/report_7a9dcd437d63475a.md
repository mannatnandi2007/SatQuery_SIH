# SatQuery AI — Remote Sensing Inspection Report
**Report ID:** `7a9dcd437d63475a`  
**Timestamp:** `2026-09-07T17:47:32.794856+00:00`  
**System Version:** `SatQuery AI v2.4 (Cobalt Telemetry)`  
**Specialist Model:** `Processed by Siamese DL Engine (Siamese CNN (ONNX)) + Gemini 2.5 Flash`

---

## 1. Query & Ingestion Metadata

- **Visual Query:** Detect changes between T1 baseline and T2 monitoring scene
- **Acquisition Count:** 2 scene(s)
  - **Scene 1:** `port_t1.jpg`
  - **Scene 2:** `port_t2.jpg`
- **Evidence Grounding:** `change_overlay`
- **Confidence Score:** **High** (0.87)

## 2. Executive Findings

> {
    "summary": "A significant transformation has occurred within the primary port infrastructure, encompassing approximately 7.6% of the total scene. This alteration, identified as a single major cluster, indicates substantial changes in surface characteristics and likely operational layout within the container terminal and adjacent port facilities.",
    "detailed_analysis": {
        "scene_overview": "The geographic footprint captures a bustling coastal

## 3. Multi-Angle Satellite Telemetry

### Scene Overview
{
    "summary": "A significant transformation has occurred within the primary port infrastructure, encompassing approximately 7.6% of the total scene. This alteration, identified as a single major cluster, indicates substantial changes in surface characteristics and likely operational layout within the container terminal and adjacent port facilities.",
    "detailed_analysis": {
        "scene_overview": "The geographic footprint captures a bustling coastal

### Land Cover & Transition (LULC)
General remote sensing scene

### Spatial & Structural Configuration
Standard geographic layout

### Spectral Indicators & Sensor Observations
Visible optical spectrum

### Operational & Environmental Risk Assessment
No critical hazards detected

## 4. Visual Evidence Artifact

![Visual Evidence Overlay](/static/overlays/change_780136114469.png)

## 5. Execution Trace & Latency Ledger

| Stage | Status | Details | Duration (ms) |
| :--- | :--- | :--- | :--- |
| Compatibility Check | OK | Validated 2 image(s) for intent: change_detection | 30.0 |
| Routing | OK | Intent: change_detection → Selected Specialist: Change Detection | 0.0 |
| Analyzing | OK | Processed by Siamese DL Engine (Siamese CNN (ONNX)) + Gemini 2.5 Flash | 21875.0 |
| Building Evidence | OK | Rendered bi-temporal comparative panel with DL contours: [54.7, 19.7, 85.4, 45.3] | 257.0 |
| Confidence Scoring | OK | Raw: 0.87 → High (0.87) | 0.0 |

**Total Duration:** `22162.0 ms`
