# SatQuery AI — Remote Sensing Inspection Report
**Report ID:** `ff3e30de2e5d4e76`  
**Timestamp:** `2026-09-07T17:17:36.191689+00:00`  
**System Version:** `SatQuery AI v2.4 (Cobalt Telemetry)`  
**Specialist Model:** `RS-VLM / Change Detection / SAR Fusion`

---

## 1. Query & Ingestion Metadata

- **Visual Query:** Execute optical and SAR radar fusion to detect metallic vessels and corner-reflecting infrastructure.
- **Acquisition Count:** 2 scene(s)
  - **Scene 1:** `port_optical_rgb.jpg`
  - **Scene 2:** `port_sentinel1_sar.jpg`
- **Evidence Grounding:** `sar_fusion`
- **Confidence Score:** **Medium** (0.65)

## 2. Executive Findings

> {
    "summary": "The fused optical and SAR observations provide a comprehensive view of a major coastal city and its active port. Optical imagery details urban infrastructure and numerous vessels, while SAR backscatter strongly corroborates these features, highlighting metallic structures and ships as high backscatter points against the specularly reflecting water. This multi-sensor intelligence confirms extensive built-up areas and dynamic maritime traffic, enabling robust detection

## 3. Multi-Angle Satellite Telemetry

### Scene Overview
{
    "summary": "The fused optical and SAR observations provide a comprehensive view of a major coastal city and its active port. Optical imagery details urban infrastructure and numerous vessels, while SAR backscatter strongly corroborates these features, highlighting metallic structures and ships as high backscatter points against the specularly reflecting water. This multi-sensor intelligence confirms extensive built-up areas and dynamic maritime traffic, enabling robust detection

### Land Cover & Transition (LULC)
General remote sensing scene

### Spatial & Structural Configuration
Standard geographic layout

### Spectral Indicators & Sensor Observations
Visible optical spectrum

### Operational & Environmental Risk Assessment
No critical hazards detected

## 4. Visual Evidence Artifact

![Visual Evidence Overlay](/static/overlays/fusion_f81dfc40e849.png)

## 5. Execution Trace & Latency Ledger

| Stage | Status | Details | Duration (ms) |
| :--- | :--- | :--- | :--- |
| Compatibility Check | OK | Validated 2 image(s) for intent: fusion | 1.0 |
| Routing | OK | Intent: fusion → Selected Specialist: Optical+SAR Fusion | 0.0 |
| Analyzing | OK | Processed by Optical-SAR Fusion (Gemini 2.5 Flash) | 25894.0 |
| Building Evidence | OK | Rendered Optical+SAR fusion overlay: None | 554.0 |
| Confidence Scoring | OK | Raw: 0.65 → Medium (0.65) | 0.0 |

**Total Duration:** `26449.0 ms`
