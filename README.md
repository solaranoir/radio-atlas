# SolaraSphere: Radio Atlas

[![Backend CI](https://github.com/solaranoir/radio-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/solaranoir/radio-atlas/actions/workflows/ci.yml)

> A beautiful, explainable, and interactive radio intelligence platform that transforms amateur radio into an explorable world.

*Observe. Explain. Predict. Replay. Explore.*

---

## Current Status

🌎 **v0.2.0 — Phase 2: Radio Weather Globe**

Phases 1 and 2 are complete.

Radio Atlas now combines a normalized radio and space-weather data foundation
with an interactive Three.js globe for exploring amateur-radio activity
geographically.

### Implemented

- NOAA space-weather data ingestion
- PSK Reporter observation ingestion
- Normalized observation storage
- FastAPI APIs
- PostgreSQL persistence
- Interactive Three.js globe
- Live observation-driven station markers
- Live signal-path visualization
- Spot-density visualization
- Solar terminator visualization
- Solar-weather visualization
- Observation filtering synchronized with globe rendering
- Station and signal-path selection
- Layer visibility controls with persisted preferences
- Keyboard globe navigation
- Reduced-motion support
- Rendering performance monitoring
- Unit, end-to-end, and visual regression testing

### Current Release

**v0.2.0** establishes the Radio Weather Globe and completes the live
observation-to-visualization pipeline.

Historical replay, production propagation predictions, AI-driven explanations,
and additional analytical capabilities remain planned for subsequent phases.

---

## Vision

Radio Atlas reimagines amateur radio software as a scientific exploration
platform rather than a collection of disconnected utilities, aging desktop
interfaces, spreadsheets, charts, and log windows.

Signals become animated pathways.

Propagation behaves like weather.

Contacts become stories.

Space weather becomes an explorable layer rather than a collection of
numerical indices.

The goal is to build a beautiful, functional, and educational visualization
platform for exploring amateur radio and the physical systems that shape it.

---

## Core Product Pillars

### Observe

Visualize live radio activity on a global scale.

### Explain

Use evidence-grounded AI to explain why radio events occur.

### Predict

Forecast likely propagation opportunities.

### Replay

Reconstruct historical propagation through time.

### Explore

Transform invisible radio phenomena into an interactive environment.

---

## Radio Weather Globe

The Radio Weather Globe is the primary visualization environment for Radio
Atlas.

Live observations flow from the application data layer through filtering and
visualization adapters into the Three.js renderer:

```text
Radio observations
        │
        ▼
Observation filtering
        │
        ▼
Visualization adapter
        │
        ├──► Station markers
        │
        ├──► Signal paths
        │
        └──► Spot density
        │
        ▼
Three.js globe
```

The renderer remains separate from API retrieval and application state. React
coordinates data and user interaction while the rendering layer manages the
Three.js scene and visualization objects.

### Current Globe Capabilities

- Interactive Earth visualization
- Mouse and keyboard camera navigation
- Live observation-driven stations
- Great-circle signal paths
- Signal strength visualization derived from observation SNR
- Geographic spot-density visualization
- Solar terminator
- Solar-weather overlays
- Layer visibility controls
- Persisted layer preferences
- Observation filters
- Station and signal-path selection
- Information panels
- Reduced-motion behavior
- Rendering performance monitoring

---

## Product Roadmap

Radio Atlas is being built incrementally, with each phase adding capabilities
to the same underlying data and visualization platform.

### ✅ Phase 1 — Foundation & Data Platform

Established the backend and data architecture.

Key work included:

- Backend architecture
- Docker development environment
- Continuous integration
- PostgreSQL and Redis infrastructure
- NOAA provider integration
- PSK Reporter integration
- Observation normalization
- Provider abstraction
- Repository layer
- FastAPI endpoints
- Health and ingestion infrastructure
- Automated backend testing

Released as **v0.1.0**.

### ✅ Phase 2 — Radio Weather Globe

Established the interactive visualization platform.

Key work included:

- Three.js globe rendering
- Earth and lighting visualization
- Camera navigation
- Signal-path rendering
- Station markers
- Spot-density visualization
- Solar terminator
- Solar-weather layers
- Layer architecture and controls
- Observation filtering
- Selection and interaction behavior
- Animation infrastructure
- Reduced-motion support
- Rendering performance monitoring
- Live observation-to-renderer integration
- Unit testing
- End-to-end browser testing
- Visual regression testing
- Globe architecture documentation

Released as **v0.2.0**.

### 🔭 Future Phases

Planned capabilities include:

- Historical propagation replay
- Timeline controls and time scrubbing
- Propagation analytics
- Production prediction paths
- Band forecasting
- Confidence scoring
- Rare-contact and anomaly intelligence
- Evidence-grounded AI explanations
- QSO story generation
- Expanded accessibility validation
- Deployment and production hardening

---

## Planned Product Capabilities

The following capabilities describe the broader Radio Atlas vision. Some are
implemented today, while others belong to later roadmap phases.

### Radio Weather Globe

**Implemented**

- Live signal paths
- Station visualization
- Spot density
- Solar terminator
- Solar-weather overlays
- Animated visualization
- Layer management
- Observation filtering
- Interactive selection

### QSO Story Engine

**Planned**

- Evidence-grounded narratives
- Propagation explanations
- Historical comparisons
- Educational explanations

### Band Forecasting

**Planned**

- Opening probabilities
- Geographic forecasts
- Confidence scoring
- Predicted propagation paths

### Historical Replay

**Planned**

- Timeline controls
- Time scrubbing
- Propagation reconstruction
- Historical exploration

### Rare Contact Discovery

**Planned / Foundational infrastructure present**

- Anomaly detection
- Contact intelligence
- Achievement generation
- Statistical analysis

---

## Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | React 19 |
| Frontend Language | TypeScript |
| Globe Rendering | Three.js |
| Frontend State | Zustand |
| Frontend Build | Vite |
| Backend | FastAPI |
| Backend Language | Python 3.12+ |
| Database | PostgreSQL |
| Cache | Redis |
| Data Sources | NOAA + PSK Reporter |
| Backend Testing | Pytest |
| Frontend Testing | Vitest + React Testing Library |
| Browser Testing | Playwright |
| Containerization | Docker |

The Phase 2 globe visualization stack is standardized on **Three.js**.
Visualization data is adapted outside the renderer and supplied explicitly to
rendering layers.

---

## Architecture

Radio Atlas separates external data acquisition, domain modeling, application
state, and visualization.

At a high level:

```text
External Data Sources
        │
        ├── NOAA
        └── PSK Reporter
        │
        ▼
Provider / Ingestion Layer
        │
        ▼
Normalized Domain Models
        │
        ▼
PostgreSQL
        │
        ▼
FastAPI
        │
        ▼
React Application
        │
        ├── Filtering
        ├── State
        ├── Analysis
        └── Visualization Adapters
                │
                ▼
           Three.js Renderer
                │
                ├── Stations
                ├── Signal Paths
                ├── Spot Density
                ├── Solar Terminator
                ├── Solar Weather
                ├── Prediction Paths
                └── Anomalies
```

The rendering context does not retrieve API data directly. Application data is
transformed into renderer-facing visualization models before crossing the
React-to-Three.js boundary.

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 24
- npm
- Docker Desktop or Docker Engine
- Docker Compose
- Git

The repository includes an `.nvmrc` for the frontend Node.js version.

### Clone the Repository

```bash
git clone git@github.com:solaranoir/radio-atlas.git
cd radio-atlas
```

### Configure the Environment

```bash
cp .env.example .env
```

Review `.env` and update local settings if necessary.

### Start the Development Stack

```bash
docker compose up --build
```

### Local Services

| Service | Address |
| --- | --- |
| FastAPI | `http://localhost:8000` |
| OpenAPI Documentation | `http://localhost:8000/docs` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

### Stop the Development Stack

```bash
docker compose down
```

---

## Frontend Development

The Radio Weather Globe lives in the `frontend` application.

```bash
cd frontend
npm install
npm run dev
```

### Frontend Validation

Run the unit test suite:

```bash
npm test -- --run
```

Run linting:

```bash
npm run lint
```

Run the production build:

```bash
npm run build
```

Run end-to-end tests:

```bash
npm run test:e2e
```

Run visual regression tests:

```bash
npm run test:visual
```

Intentional visual changes can be reviewed and then incorporated into the
baseline with:

```bash
npm run test:visual:update
```

Visual baselines should only be updated after confirming that the rendered
change is expected.

---

## Testing

Radio Atlas uses multiple testing layers rather than relying on a single test
suite.

### Backend

Pytest covers provider behavior, normalization, domain models, repositories,
and backend application logic.

### Frontend

Vitest and React Testing Library cover application state, filtering,
visualization utilities, rendering-layer behavior, interactions, and the
React-to-Three.js integration boundary.

As of **v0.2.0**, the frontend suite contains:

- **53 test files**
- **248 passing tests**

### End-to-End

Playwright validates browser-level behavior including:

- Layer visibility and persistence
- Observation filtering
- Filter-to-renderer synchronization
- Observation-backed station selection
- Camera interaction and reset behavior

### Visual Regression

Playwright also maintains deterministic visual baselines for:

- Globe rendering
- Signal paths
- Spot-density visualization
- Full-motion animation behavior

Visual tests use deterministic API-backed observations rather than
production rendering fixtures.

---

## Repository Structure

```text
radio-atlas/
├── .github/
│   └── workflows/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   ├── ingestion/
│   │   ├── models/
│   │   ├── providers/
│   │   └── repositories/
│   ├── scripts/
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   └── globe/
│   │       ├── components/
│   │       ├── filters/
│   │       ├── hooks/
│   │       ├── interactions/
│   │       ├── layers/
│   │       ├── preferences/
│   │       ├── rendering/
│   │       ├── state/
│   │       ├── types/
│   │       └── utilities/
│   └── tests/
│       ├── e2e/
│       └── visual/
│
├── docs/
│   ├── adr/
│   ├── architecture/
│   ├── requirements/
│   ├── testing/
│   └── ux/
│
├── docker-compose.yml
└── README.md
```

---

## Documentation

The repository contains living technical and product documentation covering:

| Documentation | Purpose |
| --- | --- |
| Product Requirements | Product definition and goals |
| Engineering Roadmaps | Phase-by-phase implementation plans |
| Architecture Decision Records | Architectural decisions and rationale |
| System Architecture | Backend and application architecture |
| Globe Architecture | Three.js rendering and application boundaries |
| Component Diagrams | Major frontend component relationships |
| Layer Architecture | Globe visualization layer design |
| Sequence Diagrams | Runtime data and interaction flows |
| Animation Specification | Motion semantics and behavior |
| Testing Strategy | Verification approach |
| Phase Review Notes | Implementation findings and known limitations |

---

## Guiding Architectural Principles

- Provider abstraction
- Explicit domain boundaries
- Local-first personal data
- Evidence-grounded AI
- Domain-driven state management
- Event-based historical replay
- Semantic visualization
- Explicit React-to-renderer data flow
- Rendering concerns isolated from API retrieval
- Accessibility as a system concern rather than a final polish step

---

## Development Standards

Completed features should include, where applicable:

- Types
- Tests
- Documentation
- Error handling
- Accessibility validation
- Observability
- Updated diagrams
- Explicit data ownership
- Clear application/rendering boundaries

Changes should be validated incrementally and should not silently introduce
new architectural responsibilities into existing layers.

---

## Releases

### v0.2.0 — Radio Weather Globe

Phase 2 release establishing the interactive globe, visualization layers,
observation filtering, live observation rendering, browser testing, and globe
architecture.

### v0.1.0 — Foundation & Data Platform

Phase 1 release establishing the backend architecture, ingestion system,
normalized radio observations, persistence, APIs, and development
infrastructure.

---

## License

License selection is pending.

---

*Observe. Explain. Predict. Replay. Explore.*
