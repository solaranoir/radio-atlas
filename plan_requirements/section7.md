# 7. UI/UX Requirements

## 7.1 Design Philosophy

Radio Atlas should feel less like traditional amateur radio software and more like a modern scientific instrument for observing the ionosphere.

The user experience should combine characteristics from:

* Planetarium software
* Scientific visualization platforms
* Flight tracking systems
* Space mission control interfaces
* Geographic information systems
* Modern analytical dashboards

The application should create a sense of observation and exploration rather than data entry.

The interface should help users perceive propagation as a changing environmental system.

A user watching the application for a short period should be able to recognize:

* Where activity is increasing or decreasing
* Which paths are strengthening
* Where openings are emerging or disappearing
* How the terminator is influencing propagation
* Which conditions are observed versus predicted
* Whether anything unusual is occurring

The interface should emphasize:

* Discovery
* Temporal change
* Evidence
* Visual storytelling
* Scientific context

---

## 7.2 Design Principles

### UX-001: Visual First Design

The application shall prioritize visualization over tabular presentation.

Users should be able to understand broad propagation conditions without first reading numerical reports.

Detailed numerical data shall remain available through progressive disclosure.

---

### UX-002: Radio Weather as the Primary Mental Model

The application shall present propagation as a dynamic environmental system.

Users should perceive:

* Density
* Intensity
* Movement
* Openings
* Closures
* Forecasts
* Anomalies

The design should avoid reducing the application to a collection of independent ham-radio widgets.

---

### UX-003: Exploration Before Configuration

Users shall be able to interact with meaningful live data immediately after loading the application.

The system shall avoid requiring extensive configuration before displaying useful information.

---

### UX-004: Progressive Disclosure

The interface shall reveal complexity gradually.

Beginning users shall see simplified explanations and major patterns.

Advanced users shall be able to inspect:

* Raw observations
* Statistical evidence
* Model confidence
* Propagation metrics
* Historical comparisons

---

### UX-005: Immediate Feedback

Every interactive element shall provide immediate visual feedback.

Examples include:

* Hover states
* Selected path highlighting
* Layer transitions
* Filter changes
* Timeline scrubbing
* Forecast selection
* Anomaly inspection

---

### UX-006: Consistent Interactions

Interactive controls shall behave consistently throughout the application.

Examples include:

* Toggle switches
* Dropdown menus
* Timeline controls
* Filtering panels
* Zoom behavior
* Slide-out contextual panels

---

### UX-007: Evidence Before Interpretation

When AI-generated explanations are presented, objective data shall remain visually distinct and accessible.

The preferred hierarchy shall be:

1. Observed facts
2. Supporting evidence
3. Modeled information
4. AI interpretation
5. Related insights or achievements

AI shall not visually overshadow measured data.

---

## 7.3 Visual Design Language

### UX-008: Visual Identity

The design language shall reflect the SolaraSphere ecosystem.

The interface should communicate:

* Exploration
* Astronomy
* Cartography
* Scientific discovery
* Dynamic systems
* Modern engineering

---

### UX-009: Design Theme

The visual aesthetic shall be described as:

**Modern Observatory + Space Atlas + Digital Cartography**

The interface should avoid appearing like:

* Legacy desktop software
* Spreadsheet applications
* Traditional ham-radio dashboards
* Dense control panels assembled from unrelated widgets

---

### UX-010: Color Palette

The default visual theme shall use a dark interface.

Suggested visual directions include:

| UI Element | Visual Direction |
| --- | --- |
| Background | Deep space and observatory tones |
| Observed activity | High-clarity luminous colors |
| Predicted activity | Dashed, translucent, or lower-opacity treatments |
| Historical activity | Muted or temporal gradient treatments |
| Anomalies | Brief high-contrast flare treatment |
| Alerts | Accessible status indicators |
| Heat maps | Sequential gradients with non-color cues |

Exact colors shall be defined during visual design.

---

### UX-011: Information Provenance Styling

Observed, modeled, and interpreted data shall use visually distinct conventions.

For example:

| Information Type | Suggested Treatment |
| --- | --- |
| Observed | Solid lines and markers |
| Modeled | Dashed or translucent lines |
| Historical | Muted temporal treatment |
| AI interpreted | Labeled narrative card |
| Anomalous | Short-lived flare or pulse |

The system shall provide a visible legend.

---

## 7.4 Layout Requirements

### UX-012: Primary Layout

The default desktop layout shall include:

| Region | Purpose |
| --- | --- |
| Header | Navigation, search, live status |
| Left panel | Layers and filters |
| Center | Radio Weather Globe |
| Right contextual panel | QSO Story, anomaly details, analytics |
| Bottom panel | Timeline and replay controls |

The central globe shall remain visually dominant.

---

### UX-013: Contextual Panels

Secondary functionality shall appear through contextual slide-out or dockable panels rather than permanently occupying large areas of the screen.

Examples include:

* QSO Story
* Rare Contact Discovery
* Anomaly analysis
* Detailed solar conditions

The globe should remain visible whenever practical.

---

### UX-014: Forecast Workspace

Radio Forecast shall support an expanded analytical workspace.

The forecast experience shall be able to transition from a compact summary into a larger view that includes:

* Band rankings
* Geographic opportunities
* Forecast timeline
* Confidence values
* Predicted propagation overlays

---

### UX-015: Responsive Layout

The interface shall adapt to:

* Desktop monitors
* Laptops
* Tablets
* Smartphones

---

### UX-016: Mobile Layout

Mobile devices shall prioritize:

* Globe visualization
* Current conditions
* Layer selection
* Simplified filters
* Forecast summary

Secondary information shall appear in bottom sheets or collapsible panels.

---

## 7.5 Radio Weather Globe Experience Requirements

### UX-017: Globe as Primary Interface

The three-dimensional globe shall function as the primary interaction model.

Users shall be able to:

* Rotate the globe
* Zoom
* Select paths
* Select geographic regions
* Select anomalies
* Enable and disable overlays

---

### UX-018: Radio Weather Behaviors

The globe shall communicate changing propagation conditions through animation.

Required behaviors include:

* Regions softly pulsing according to spot density
* Paths brightening as signal conditions strengthen
* Propagation openings appearing and dissolving
* The terminator sweeping across active regions
* Historical conditions morphing during replay
* Predicted paths using a distinct visual treatment
* Anomalous paths flaring briefly

Animations shall communicate data state rather than serve decorative purposes.

---

### UX-019: Twenty-Second Readability Goal

A user observing the globe for approximately twenty seconds should be able to perceive meaningful changes in the radio environment.

The visualization should communicate:

* Growth or decline in activity
* Shifts in geographic openings
* Changes in dominant bands or paths
* Terminator influence
* Unexpected propagation events

---

### UX-020: Visual Hierarchy

Visual elements shall be prioritized in the following order:

1. Significant propagation events
2. Active radio-weather patterns
3. Selected user interactions
4. Predicted propagation
5. Geographic overlays
6. Background map features

---

### UX-021: Watch Mode

The application shall provide an optional passive observation mode.

Watch Mode shall:

* Minimize controls
* Continue live updates
* Slowly rotate or reposition the globe when appropriate
* Display optional evidence-based observational captions
* Support full-screen presentation

Watch Mode may be used for:

* Demonstrations
* Education
* Passive monitoring
* Portfolio presentation

---

## 7.6 Timeline and Propagation Time Machine Requirements

### UX-022: Historical Replay Controls

The timeline interface shall include:

* Play
* Pause
* Rewind
* Fast forward
* Playback speed
* Time selection
* Live-return control

---

### UX-023: Scrubbing

Users shall be able to drag the timeline to any point within the selected historical window.

The globe and active overlays shall update synchronously during scrubbing.

---

### UX-024: Temporal Context

Historical mode shall be visually distinct from live mode.

The current replay timestamp shall remain clearly visible.

Users shall never confuse historical data with current conditions.

---

## 7.7 AI Experience Requirements

### UX-025: QSO Story Presentation

QSO Story shall appear as a contextual right-side slide-out panel when a user selects a contact or propagation path.

The globe shall remain visible behind the panel.

---

### UX-026: Narrative Presentation

AI-generated explanations shall be:

* Readable
* Concise
* Contextual
* Evidence grounded
* Clearly labeled as interpretation

---

### UX-027: Explainability

AI explanations shall provide access to supporting evidence.

Users should understand why conclusions were generated.

Supporting evidence may include:

* Solar conditions
* Gray-line overlap
* Signal reports
* Distance
* Historical comparisons
* Rarity metrics

---

### UX-028: Explanation Depth

Users shall be able to select explanation levels such as:

* Beginner
* Educational
* Technical

---

## 7.8 Contact Intelligence and Achievement Requirements

### UX-029: Rare Contact Discovery

Rare Contact Discovery shall appear within the QSO Story or Contact Intelligence experience rather than as an independent top-level dashboard.

The interface shall identify:

* Unusual paths
* Rare geographic contacts
* Statistical outliers
* First-time contacts
* Significant distance records

---

### UX-030: Achievement Visualization

Achievements may be displayed as collectible cards.

Cards shall include:

* Achievement name
* Description
* Supporting statistic
* Completion date

---

### UX-031: Gamification

Gamification shall remain subordinate to scientific and analytical functionality.

Achievements shall not distract from propagation analysis.

---

## 7.9 Dashboard and UI Components

The following components shall be developed as independent modules:

* Radio Weather Globe
* Layer selector
* Filter panel
* Search
* Timeline
* Playback controls
* QSO Story panel
* Evidence panel
* Radio Forecast workspace
* Anomaly detail panel
* Contact Intelligence panel
* Achievement cards
* Current conditions panel
* Watch Mode presentation layer

---

## 7.10 Conceptual Desktop Layout

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ SOLARASPHERE: RADIO ATLAS       LIVE ●       Search       Forecast        │
├──────────────────┬───────────────────────────────────┬─────────────────────┤
│                  │                                   │                     │
│ Layers           │                                   │ Contextual Panel    │
│ Filters          │        RADIO WEATHER GLOBE        │                     │
│ Search           │                                   │ QSO Story           │
│                  │                                   │ Anomaly Detail      │
│                  │                                   │ Evidence            │
│                  │                                   │                     │
├──────────────────┴───────────────────────────────────┴─────────────────────┤
│ ◀◀   ▶   ▶▶    Historical Timeline / Propagation Time Machine     LIVE   │
└────────────────────────────────────────────────────────────────────────────┘
```

## 7.11 Conceptual Mobile Layout

```text
┌──────────────────────────────┐
│ RADIO ATLAS        ☰     ●   │
├──────────────────────────────┤
│                              │
│        RADIO WEATHER         │
│            GLOBE             │
│                              │
├──────────────────────────────┤
│ 20m • FT8 • LIVE             │
│ [Layers] [Filters] [Replay]  │
├──────────────────────────────┤
│ Radio Forecast               │
├──────────────────────────────┤
│ Current Conditions           │
└──────────────────────────────┘
```
