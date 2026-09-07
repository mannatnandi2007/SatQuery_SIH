# SatQuery AI — Remote Sensing Inspection Report
**Report ID:** `f639f31c4ce840ed`  
**Timestamp:** `2026-09-07T17:19:34.759428+00:00`  
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
    "summary": "The fused optical and SAR observations clearly delineate a major port city, identifying dense urban infrastructure and numerous maritime vessels as strong corner reflectors due to their metallic and structural properties. Calm water bodies exhibit characteristic specular reflection (low SAR backscatter), while urban areas and port facilities show high optical albedo correlating with intense radar returns, confirming their built-up nature.",
    "detailed_analysis": {
        "scene_overview": "The optical scene presents a high-resolution, true-color view of a sprawling coastal city, dominated by a large commercial port with extensive infrastructure and numerous ships. The SAR radar backscatter scene, co-registered, highlights areas of high microwave reflectivity (bright) corresponding to urban structures and vessels, and areas of low reflectivity (dark) corresponding to calm water surfaces, effectively penetrating any atmospheric haze or cloud cover if present.",
        "land_cover": "Land cover classification reveals dense urban built-up areas and port facilities characterized by high optical albedo (concrete, roofs) and very high SAR backscatter (buildings, cranes, containers). Water bodies (ocean, river) show low optical albedo (dark blue) and extremely low SAR backscatter, indicative of specular reflection from smooth surfaces. Limited vegetated areas within the urban fabric exhibit moderate optical albedo and slightly elevated, textured SAR backscatter.",
        "key_objects": [
            "High-backscatter metallic / structural corner reflector: Numerous large cargo vessels and container ships docked and navigating within the port (Bottom-Left, Bottom-Right quadrants). Dense clusters of urban buildings and high-rise structures throughout the city (Top-Left, Top-Right, Bottom-Left quadrants).",
            "Specular low-backscatter feature: The expansive ocean/bay surface surrounding the port (Bottom-Left, Bottom-Right quadrants) and the river channel traversing the city (Top-Left, Top-Right quadrants).",
            "Volume scattering canopy or rough terrain: Small vegetated park areas and tree lines interspersed within the urban environment (e.g., visible green patches in Top-Left, Top-Right, and Bottom-Left quadrants)."
        ],
        "spatial_patterns": "Radar backscatter intensity is spatially concentrated and very high across the dense urban core and the entire port complex, outlining individual buildings, docks, and vessels with sharp, bright returns. Conversely, all open water bodies exhibit consistently low backscatter, appearing as dark, smooth regions. Roads and open paved areas show moderate backscatter, distinct from both water and intense building returns.",
        "spectral_

## 3. Multi-Angle Satellite Telemetry

### Scene Overview
{
    "summary": "The fused optical and SAR observations clearly delineate a major port city, identifying dense urban infrastructure and numerous maritime vessels as strong corner reflectors due to their metallic and structural properties. Calm water bodies exhibit characteristic specular reflection (low SAR backscatter), while urban areas and port facilities show high optical albedo correlating with intense radar returns, confirming their built-up nature.",
    "detailed_analysis": {
        "scene_overview": "The optical scene presents a high-resolution, true-color view of a sprawling coastal city, dominated by a large commercial port with extensive infrastructure and numerous ships. The SAR radar backscatter scene, co-registered, highlights areas of high microwave reflectivity (bright) corresponding to urban structures and vessels, and areas of low reflectivity (dark) corresponding to calm water surfaces, effectively penetrating any atmospheric haze or cloud cover if present.",
        "land_cover": "Land cover classification reveals dense urban built-up areas and port facilities characterized by high optical albedo (concrete, roofs) and very high SAR backscatter (buildings, cranes, containers). Water bodies (ocean, river) show low optical albedo (dark blue) and extremely low SAR backscatter, indicative of specular reflection from smooth surfaces. Limited vegetated areas within the urban fabric exhibit moderate optical albedo and slightly elevated, textured SAR backscatter.",
        "key_objects": [
            "High-backscatter metallic / structural corner reflector: Numerous large cargo vessels and container ships docked and navigating within the port (Bottom-Left, Bottom-Right quadrants). Dense clusters of urban buildings and high-rise structures throughout the city (Top-Left, Top-Right, Bottom-Left quadrants).",
            "Specular low-backscatter feature: The expansive ocean/bay surface surrounding the port (Bottom-Left, Bottom-Right quadrants) and the river channel traversing the city (Top-Left, Top-Right quadrants).",
            "Volume scattering canopy or rough terrain: Small vegetated park areas and tree lines interspersed within the urban environment (e.g., visible green patches in Top-Left, Top-Right, and Bottom-Left quadrants)."
        ],
        "spatial_patterns": "Radar backscatter intensity is spatially concentrated and very high across the dense urban core and the entire port complex, outlining individual buildings, docks, and vessels with sharp, bright returns. Conversely, all open water bodies exhibit consistently low backscatter, appearing as dark, smooth regions. Roads and open paved areas show moderate backscatter, distinct from both water and intense building returns.",
        "spectral_

### Land Cover & Transition (LULC)
General remote sensing scene

### Spatial & Structural Configuration
Standard geographic layout

### Spectral Indicators & Sensor Observations
Visible optical spectrum

### Operational & Environmental Risk Assessment
No critical hazards detected

## 4. Visual Evidence Artifact

![Visual Evidence Overlay](/static/overlays/fusion_28496bd21b16.png)

## 5. Execution Trace & Latency Ledger

| Stage | Status | Details | Duration (ms) |
| :--- | :--- | :--- | :--- |
| Compatibility Check | OK | Validated 2 image(s) for intent: fusion | 1.0 |
| Routing | OK | Intent: fusion → Selected Specialist: Optical+SAR Fusion | 0.0 |
| Analyzing | OK | Processed by Optical-SAR Fusion (Gemini 2.5 Flash) | 31978.0 |
| Building Evidence | OK | Rendered Optical+SAR fusion overlay: None | 532.0 |
| Confidence Scoring | OK | Raw: 0.65 → Medium (0.65) | 0.0 |

**Total Duration:** `32511.0 ms`
