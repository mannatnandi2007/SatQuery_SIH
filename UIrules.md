# SatQuery AI — Hallmark UI & UX Design Rules

**Document:** `UIrules.md`  
**Purpose:** Strict visual and interaction guidelines for the SatQuery AI Remote Sensing Telemetry Workbench.  
**Lead Designer:** Aryan  
**Design Standard:** Hallmark Anti-AI-Slop Specification v1.1.0  

---

## 1. The Core Hallmark Philosophy

SatQuery AI is a professional Earth Observation and Remote Sensing Telemetry Workbench, not a generic consumer AI marketing landing page. The design must look **made, engineered, and tactile**—never generated from predictable LLM boilerplate templates.

Every interface component must prioritize:
- **Information Density & Clarity:** Immediate visibility of critical geospatial parameters (GSD, bounding coordinates, sensor band, confidence score).
- **Tactile High-Contrast Surfaces:** Solid, opaque paper band surfaces with razor-sharp borders instead of blurry, floating cards.
- **Structural Variety:** An intentional industrial workbench layout—dual-canvas imagery viewer, real-time observable telemetry drawer, and modular inspector sidebar—rather than the cliché Hero → 3 Feature Cards → CTA footer rhythm.

---

## 2. The 20 Banned UI Patterns (Strict Negative Constraints)

The following 20 patterns represent the most pervasive clichés in AI web generation. **Their presence anywhere in this codebase is strictly forbidden:**

| # | Banned Anti-Pattern | Reason for Ban & Rejection | Approved Replacement |
|---|---|---|---|
| 1 | **NO purple to blue gradient** | Ubiquitous "AI SaaS" default background gradient that screams generic boilerplate. | Solid tactile paper tones (`oklch(14% 0.01 250)`) or single-hue monochromatic luminance shifts. |
| 2 | **NO untouched shadcn ui** | Stock copy-pasted component libraries with identical padding, default zinc borders, and zero brand personality. | Purpose-built geospatial workbench components with crisp 4px/6px radii, bespoke tokens, and compact data density. |
| 3 | **NO gradient hero text** | Text clipped over a multi-color gradient (`background-clip: text; color: transparent`). Low legibility and extreme AI tell. | Solid high-contrast roman typography in pure ink (`--color-ink`) or calibrated brand accent. |
| 4 | **NO Fade in on scroll** | Sluggish `IntersectionObserver` scroll animations that delay content display and frustrate technical users. | Instant render. If content updates, use instant or rapid ($<150\text{ms}$) deterministic state transitions. |
| 5 | **NO emojis on heading** | Decorative emojis prefixing or suffixing headers (e.g. `🛰️ SatQuery`, `✨ AI Results`). | Crisp technical headers, alphanumeric tags (`SEC-01`, `STAGE-03`), or functional SVG symbols. |
| 6 | **NO cursor following beam** | Distracting mouse-following spotlight glow or radial gradient beam tracing the pointer. | Zero pointer-following decoration. The pointer is a precision GIS inspection instrument. |
| 7 | **NO inter font everywhere** | Lazy fallback font of every website built in the last 6 years. Zero personality. | Intentional pairings: `Plus Jakarta Sans`, `IBM Plex Sans`, or `Outfit` for UI body, paired with `JetBrains Mono` for telemetry. |
| 8 | **NO button fades on hover** | Mushy, gradual opacity or background-color fades on hover that feel unresponsive. | Tactile mechanical buttons: crisp 1px active press displacement (`transform: translateY(1px)`), instant hover step, and high-contrast focus rings. |
| 9 | **NO colored bordered cards** | Gimmicky neon cyan, purple, or green 1px borders surrounding standard cards. | Structural separation via distinct background paper steps (`--color-paper-2`, `--color-paper-3`) and hairline neutral rules (`--color-rule`). |
| 10 | **NO inconsistent spacing** | Arbitrary, unconstrained margins and paddings (e.g. 13px, 21px, 37px). | Strict adherence to the 4-pt / 8-pt spacing scale token system (`4px`, `8px`, `12px`, `16px`, `24px`, `32px`, `48px`). |
| 11 | **NO Glass morphism cards** | Blurry frosted glass cards (`backdrop-filter: blur(12px)` over transparent rgba) causing poor contrast and GPU churn. | Solid, opaque, structured surfaces with verified WCAG AAA contrast ratios against text. |
| 12 | **NO Em dashes everywhere** | Compulsive use of em dashes (`—`) littered across every paragraph and headline by default LLM copy generators. | Concise, disciplined sentences, colons, or clean bullet points. |
| 13 | **NO Low contrast dark mode** | Muddy, illegible dark mode where dark gray text sits on slightly darker gray backgrounds (#71717A on #18181B). | High-contrast dark mode: stark high-contrast ink (`oklch(96% 0.005 250)`), high-visibility border rules (`oklch(28% 0.015 255)`), and vibrant status chips. |
| 14 | **NO generic buzzword copy** | Fluff like "Supercharge your satellite analysis with next-generation deep intelligence". | Honest, factual technical copy: "Multi-sensor Ground Sampling Distance normalization and localized visual question answering for Earth Observation." |
| 15 | **NO 3 icon boxed in a row** | The standard 3-box feature grid with an icon floating inside a rounded square on top. | Asymmetric information architecture: split-pane geospatial inspector, live telemetry feeds, and interactive parameter tables. |
| 16 | **NO serif italic accents** | Italicized serif emphasis words inside otherwise upright sans headers (`Built to <em>revolutionize</em>`). | Roman-only headings (`font-style: normal`). Emphasis is conveyed via font-weight, color accent, or deliberate underline. |
| 17 | **NO badge above headline** | The cliché floating pill badge placed right above the primary title (`[✦ New Release 2.0]`). | Integrated application status bar with active engine status, memory footprint, and sensor connectivity. |
| 18 | **NO space grotesk and instrument serif** | The overused 2024-2025 "creative agency / Web3 / AI slop" typeface combination. | Banned completely. Approved alternatives: `Cabinet Grotesk` or `Syne` for display headers, paired with `Plus Jakarta Sans` or `IBM Plex Sans`. |
| 19 | **NO lucide icons everywhere** | Sprinkling generic icons next to every label, button, and table row for decorative decoration. | Icons must be strictly functional (e.g., pan, zoom, upload, inspect, download). If text is clear without an icon, omit the icon. |
| 20 | **NO grain over gradient** | SVG turbulence noise filters layered on top of dark gradients to fake texture. | Clean, high-performance solid surfaces with crisp geometric hair-lines and precise coordinate grids. |

---

## 3. Approved Typography & Font Hierarchy

```css
/* Hallmark Approved Font Stack — Strict Roman Headers & Monospace Telemetry */
:root {
    /* Primary UI Body: Clean, legible, high-density sans */
    --font-body: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    
    /* Technical Telemetry & Metadata: Monospace with tabular numbers */
    --font-mono: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace;
    
    /* Display / Technical Headers: Rugged industrial grotesque, strictly roman (NO italics) */
    --font-display: 'Cabinet Grotesk', 'Syne', -apple-system, sans-serif;
}
```

### Typographic Rules
1. **Zero Italic Headers:** All `h1`, `h2`, `h3`, `h4`, and display titles MUST specify `font-style: normal;`. Emphasis is achieved via weight (`700`), accent color, or a 1px baseline rule.
2. **Tabular Numbers for Telemetry:** All durations, coordinates, bounding box percentages, and confidence scores MUST declare `font-variant-numeric: tabular-nums;` to prevent layout jitter during updates.
3. **Strict Hierarchy Scale:**
   - Display Title: `24px` to `28px`, letter-spacing `-0.02em`, weight `700`.
   - Section Headings: `14px` to `16px`, letter-spacing `-0.01em`, weight `600`, uppercase with `0.05em` tracking for sub-panels.
   - Body & Controls: `13px` to `14px`, line-height `1.5`, weight `400` / `500`.
   - Telemetry & Micro-Labels: `11px` to `12px`, `font-mono`, weight `500`.

---

## 4. Design Tokens & High-Contrast Color Palette

All color declarations MUST reference named CSS custom properties. Direct inline hex, rgb, or improvised OKLCH declarations outside `:root` are strictly forbidden.

```css
:root, [data-theme="dark"] {
    /* Paper Bands (Solid, Opaque Surface Layers) */
    --color-paper: oklch(14% 0.012 255);       /* Deep workbench base */
    --color-paper-2: oklch(18% 0.015 255);     /* Panel & canvas container */
    --color-paper-3: oklch(22% 0.018 255);     /* Hover surface / active panel */
    --color-paper-elevated: oklch(26% 0.02 255);/* Dropdowns & floating toolbars */

    /* Structural Hairline Rules */
    --color-rule: oklch(28% 0.015 255);        /* Standard panel divider */
    --color-rule-subtle: oklch(22% 0.01 255);  /* Minor internal grid lines */
    --color-rule-strong: oklch(40% 0.025 255); /* Active or focused panel borders */

    /* Typography Ink Tiers (High Contrast WCAG AAA) */
    --color-ink: oklch(96% 0.005 250);         /* Primary crisp white text */
    --color-ink-2: oklch(80% 0.01 250);        /* Secondary descriptive labels */
    --color-muted: oklch(62% 0.012 250);       /* Micro-telemetry & timestamps */

    /* Telemetry Accent (High-Visibility Marine Blue / Cyan) */
    --color-accent: oklch(68% 0.18 235);
    --color-accent-hover: oklch(74% 0.19 235);
    --color-accent-active: oklch(62% 0.20 235);
    --color-accent-ink: oklch(10% 0.01 255);
    --color-accent-subtle: oklch(68% 0.18 235 / 0.12);

    /* Functional Status Semantics */
    --status-success: oklch(72% 0.18 145);      /* Validated / High Confidence */
    --status-success-bg: oklch(72% 0.18 145 / 0.12);
    --status-warning: oklch(78% 0.16 75);       /* GSD Scale Mismatch / Medium Conf */
    --status-warning-bg: oklch(78% 0.16 75 / 0.12);
    --status-error: oklch(65% 0.22 25);         /* Compatibility Failure / Pipeline Error */
    --status-error-bg: oklch(65% 0.22 25 / 0.12);

    /* Spacing System (Strict 4-pt / 8-pt Scale) */
    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-6: 24px;
    --space-8: 32px;
    --space-12: 48px;

    /* Geometry */
    --radius-xs: 3px;
    --radius-sm: 5px;
    --radius-md: 8px;
}
```

---

## 5. Mandatory 8-State Interactive Component Checklist

Every interactive component (Buttons, Inputs, Selectors, Tabs, Toggles) MUST explicitly implement styles for all **8 interactive states**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      8-STATE INTERACTIVE LIFECYCLE                     │
├───────────────┬────────────────────────────────────────────────────────┤
│ 1. default    │ Base resting state with verified contrast              │
│ 2. hover      │ Step background to --color-paper-3, crisp rule change   │
│ 3. focus-vis  │ 2px solid --color-accent outline with 2px offset       │
│ 4. active     │ Mechanical press: transform: translateY(1px)           │
│ 5. disabled   │ cursor: not-allowed, opacity: 0.45, zero pointer-ev   │
│ 6. loading    │ Deterministic progress indicator or pulsing mono text  │
│ 7. error      │ 1px solid --status-error, inline error diagnostic pill │
│ 8. success    │ 1px solid --status-success, confirmation status badge  │
└───────────────┴────────────────────────────────────────────────────────┘
```

### CSS Implementation Example (Mechanical Tactile Button)
```css
.btn-workbench {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    font-family: var(--font-body);
    font-size: 13px;
    font-weight: 600;
    line-height: 1;
    color: var(--color-ink);
    background: var(--color-paper-2);
    border: 1px solid var(--color-rule);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: background 80ms ease, border-color 80ms ease;
    user-select: none;
}

/* 2. Hover */
.btn-workbench:hover:not(:disabled) {
    background: var(--color-paper-3);
    border-color: var(--color-rule-strong);
}

/* 3. Focus Visible */
.btn-workbench:focus-visible {
    outline: 2px solid var(--color-accent);
    outline-offset: 2px;
}

/* 4. Active (Mechanical Click) */
.btn-workbench:active:not(:disabled) {
    transform: translateY(1px);
    background: var(--color-paper);
}

/* 5. Disabled */
.btn-workbench:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    pointer-events: none;
}

/* 6. Loading */
.btn-workbench[data-state="loading"] {
    cursor: wait;
    opacity: 0.8;
}

/* 7. Error */
.btn-workbench[data-state="error"] {
    border-color: var(--status-error);
    color: var(--status-error);
}

/* 8. Success */
.btn-workbench[data-state="success"] {
    border-color: var(--status-success);
    color: var(--status-success);
}
```

---

## 6. Layout Architecture: Industrial Telemetry Workbench

Instead of standard stacked landing-page sections, SatQuery AI uses a **three-pane telemetry workbench**:

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ APPLICATION HEADER: System Telemetry Bar (Status, GSD Engine, Model State, Session)  │
├──────────────────────────┬─────────────────────────────────┬──────────────────────────┤
│ LEFT PANEL: INPUTS       │ CENTER STAGE: DUAL-CANVAS       │ RIGHT PANEL: INSPECTOR   │
│                          │                                 │                          │
│ • Sensor & Mode Toggle   │ [ Raw Image ]  [ Evidence View ] │ • Grounded Answer Box    │
│ • Drag & Drop GeoTIFF    │                                 │ • Physical Dimensions    │
│ • GSD Normalizer Control │ • Bounding Box Overlay          │ • Object Class Hierarchy │
│ • Natural Language Query │ • Metric Scale Bar (100m)       │ • Confidence Meter (89%) │
│ • Execute Button         │ • Synchronized Crosshair Pan    │ • Export Report (PDF/MD) │
├──────────────────────────┴─────────────────────────────────┴──────────────────────────┤
│ BOTTOM DRAWER: Observable Execution Telemetry Trace (Timing ms, Stage Diagnostics)    │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Responsiveness & Slop-Test Pre-Emit Verification

Before releasing any UI code or changes, verify the implementation against the following non-negotiable checks:

- [ ] **Root Overflow Protection:** `html, body { overflow-x: clip; }` applied; zero horizontal layout shifting across any screen width.
- [ ] **Breakpoints Tested:** Flawless rendering verified at **320px**, **375px**, **768px**, and **1440px**.
- [ ] **No Two-Line Interactive Text:** All buttons, nav items, and telemetry chips fit on a single line without wrapping.
- [ ] **Zero Banned Elements:** Explicitly check code to ensure none of the 20 banned patterns appear in any CSS or HTML template.
- [ ] **Pre-Emit Score:** Stamp code with Hallmark critique scores:
  ```css
  /* Hallmark · genre: modern-minimal · macrostructure: Workbench · theme: cobalt */
  /* Pre-emit critique: Philosophy:5 Hierarchy:5 Execution:5 Specificity:5 Restraint:5 Variety:5 */
  ```
