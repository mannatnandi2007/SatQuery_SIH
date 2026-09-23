# SAT QUERY — UI Update Report

SAT QUERY is an AI-powered satellite imagery analysis and research platform. This document serves as a technical report detailing the frontend and UI modernization applied to the project. The primary goal of this update was to establish a premium, cinematic entry experience and refine the existing analysis workbench, all while strictly preserving the existing backend analysis pipeline and API functionality.

## 2. TECHNOLOGIES USED

### Frontend
- React
- Vite
- JavaScript (JSX)
- CSS (Vanilla, with variables for design tokens)
- Three.js
- React Three Fiber (`@react-three/fiber`)
- Drei (`@react-three/drei`)
- Lucide React (for iconography)

### Backend
- Python
- FastAPI
- Uvicorn (ASGI server)
- ONNX Runtime
- Pillow (PIL)
- OpenCV (`opencv-python-headless`)
- Generative AI Integrations: Gemini (`google-generativeai`) and Groq (`groq`)

### AI / Computer Vision
- ONNX models
- JEPA Engine (`jepa_engine.py`)

### Development / Build
- npm
- Vite (Frontend Build Tool)
- Python virtual environment (`venv`)
- Git / GitHub

## 3. PREVIOUS UI

The original interface primarily focused directly on the analysis workbench. Users were immediately presented with a dense command-center dashboard containing the following components:
- Header
- IngestionPanel
- CanvasInspector
- ExecutiveSummary
- SuggestionChips
- FeedbackStrip
- TelemetryDrawer
- ReportModal

While functional, it lacked an introductory landing experience that communicated the platform's advanced AI capabilities before users engaged with the complex tools.

## 4. NEW UI ARCHITECTURE

The application flow has been redesigned into a progressive disclosure model:

Landing Page
      ↓
User Query + Image Upload
      ↓
Processing View
      ↓
FastAPI `/query` (via Pipeline)
      ↓
Analysis Workbench
      ↓
Results / Evidence / Reports

The new Landing Page now acts as the premium entry point to SAT QUERY, seamlessly transitioning the user through a processing state before arriving at the existing Analysis Workbench. The Workbench remains the functional environment for deep inspection and evidence review.

## 5. LANDING PAGE UPDATE

The landing experience was completely rebuilt to provide a cinematic, interactive introduction.

### SAT QUERY Branding
- Prominent SAT QUERY branding.
- Tagline: *"Satellite Intelligence, Simplified."*
- Call to Action: *"Explore. Ask. Discover."*

### Chat Interface
- Centralized natural-language query input field.
- Integrated image upload handling.
- Quick action prompt chips.
- Seamless query submission that routes directly into the processing pipeline.

### Earth Visualization
- A 3D interactive background powered by Three.js, React Three Fiber, and Drei.
- Features a highly detailed rotating `EarthCanvas` and `EarthScene` utilizing distinct textures (bump map, clouds, day, and night textures).
- The scene includes atmospheric glow and a dedicated `SatelliteLayer` displaying orbiting satellites with trailing orbital paths.
- The 3D scene provides a cinematic, technical aesthetic that elevates the perceived value of the product upon first load.

## 6. PROCESSING VIEW

The `ProcessingView` is a full-screen transition state that bridges the gap between the initial landing query and the final workbench rendering.
- It features a full-screen dark layout with the SAT QUERY branding.
- Displays a central *"Analyzing satellite data..."* primary message.
- Utilizes an animated, pulsing radial glow background and a scanning loader bar (`.processing-loader-bar`).
- Iterates through dynamic processing status messages (e.g., "Routing query...", "Inspecting imagery...") to provide feedback during backend processing.
- The view automatically transitions to the Workbench once the real API request resolves.

## 7. IMAGE UPLOAD AND QUERY FLOW

The user flow is now orchestrated as follows:
1. The user enters a natural-language query on the Landing Page.
2. The user attaches satellite imagery via the Chat Interface.
3. The frontend validates that at least one file is attached.
4. The `ProcessingView` appears and the loading animation begins.
5. The frontend constructs a request using `FormData` containing the file(s) and query string.
6. The request is sent to the existing backend pipeline via the `queryPipeline` service function (targeting the `/query` endpoint, though wrapped in the pipeline logic).
7. The backend processes the request using its specialists and models.
8. The API response is returned and stored in the frontend state.
9. The application view flips to the Workbench, rendering the results.

## 8. WORKBENCH UI UPDATE

The core Analysis Workbench retained its 3-column architecture but received significant visual modernization to align with the premium landing page.

### Left Pane
Contains the `IngestionPanel`, providing input, imagery, and query controls.

### Center Pane
Contains the `CanvasInspector`, which is responsible for rendering the satellite imagery and visual evidence overlays.

### Right Pane
Contains the `ExecutiveSummary` and `SuggestionChips`, providing analysis summaries, confidence scores, detected object details, and intelligent follow-up query suggestions.

The visual styling (spacing, typography, borders, and glassmorphism) was heavily updated to create a cohesive aesthetic, completely preserving the underlying analysis logic and state management.

## 9. VISUAL DESIGN SYSTEM

A strict visual language was applied across the application:

### Colors
- **Foundation:** Dark navy/black backgrounds (`#020611`).
- **Typography:** White and light-gray text for high legibility.
- **Accent:** Warm orange (`#ff7b00`) used for branding and critical interactive elements.
- **Evidence:** Blue/cyan tones used for telemetry, grounding elements, and secondary highlights.

### Design Characteristics
- Glassmorphism applied to primary panels (e.g., Header, ChatPanel, ExecutiveSummary).
- Minimalist 1px subtle borders (using fractional opacity).
- A cinematic satellite aesthetic emphasizing space and depth.
- Clean, responsive layouts.
- Technical/monospace typography used for telemetry, confidence scores, and raw data display.

## 10. RESPONSIVE DESIGN

The application incorporates responsive CSS to ensure usability across devices:
- Layouts gracefully collapse via `@media (max-width: 1023px)` and `@media (max-width: 768px)` breakpoints.
- The 3-column Workbench transitions into a stacked column layout on smaller screens.
- The Processing View card and Chat Interface scale down dynamically to fit mobile viewports.

## 11. FILES / COMPONENTS UPDATED

The modernization touched several key areas of the frontend architecture:

### New Files
- `frontend/src/components/LandingPage.jsx`: The new cinematic entry point for the application.
- `frontend/src/components/ChatPanel.jsx`: The central input interface for queries and image uploads.
- `frontend/src/components/EarthCanvas.jsx`: The Three.js wrapper component for the 3D scene.
- `frontend/src/components/EarthScene.jsx`: The inner logic handling Earth rendering, textures, and rotation.
- `frontend/src/components/SatelliteLayer.jsx`: The Three.js logic for orbiting satellites and trails.
- `frontend/src/components/ProcessingView.jsx`: The transition loading screen between landing and workbench.
- `frontend/public/assets/earth/*`: High-resolution textures used for the 3D Earth.

### Modified Files
- `frontend/src/App.jsx`: Updated to handle routing state (`landing`, `processing`, `workbench`) and pass query data between components.
- `frontend/src/index.css`: Massively expanded to include new design tokens, animations, landing page styles, and 3D canvas overlay rules.
- `frontend/src/components/Header.jsx`: Updated visual styling to match the new dark glassmorphic design system.
- `frontend/src/components/IngestionPanel.jsx`: Refined layout and spacing.
- `frontend/src/components/ExecutiveSummary.jsx`: Modernized typography, spacing, and border treatments.
- `frontend/package.json` / `package-lock.json`: Added Three.js and React Three Fiber dependencies.

### Preserved Files
- `frontend/src/components/CanvasInspector.jsx`: Geospatial rendering logic remains untouched.
- `frontend/src/components/FeedbackStrip.jsx`: Telemetry reporting untouched.
- `frontend/src/components/ReportModal.jsx`: Report generation untouched.

## 12. BACKEND PRESERVATION

This update was strictly a UI/Frontend modernization. It completely preserved:
- The FastAPI backend architecture.
- The existing API contract and `/query` endpoint.
- The complex multi-model analysis pipeline (JEPA, ONNX, LLM).
- Evidence generation, confidence data mapping, and detected object structuring.
- Report functionality, telemetry data, and user feedback mechanisms.

The new UI was cleanly wrapped around the existing backend to elevate the user experience without compromising any scientific or analytical functionality.

## 13. SECURITY / ENVIRONMENT VARIABLES

Sensitive credentials, such as Gemini and Groq API keys, are kept strictly outside of source control. The repository relies on `.env` files for local configuration, and provides an `.env.example` file to document required variables without exposing secrets.

## 14. BUILD / VALIDATION

The frontend was rigorously tested and built using Vite.
- Validation: `npm run build` executed successfully without compilation errors.
- The production bundles were successfully generated, confirming that the new React Three Fiber dependencies integrate flawlessly with the existing build pipeline.

## 15. CURRENT STATUS

| Area | Status |
|------|--------|
| Landing UI | Complete |
| Earth visualization | Complete |
| Satellite animation | Complete |
| Image upload | Complete |
| Processing view | Complete |
| API integration | Complete |
| Analysis workbench | Complete |
| Responsive UI | Complete |
| Reports/export | Existing |

## 16. FUTURE IMPROVEMENTS

*(FUTURE / PLANNED)*
While the current UI is highly capable, future iterations may include:
- **Richer AI processing visualization:** Expanding the processing view to show real-time telemetry from the backend models.
- **Additional satellite visualization modes:** Adding interactive data layers (e.g., thermal, infrared) directly onto the 3D Earth.
- **Improved mobile layout:** Further optimizing the CanvasInspector for touch interactions on mobile devices.
- **Advanced evidence visualization:** Rendering 3D bounding boxes or confidence heatmaps in the Workbench.
- **Accessibility improvements:** Expanding ARIA labels and keyboard navigation for complex geospatial tools.
