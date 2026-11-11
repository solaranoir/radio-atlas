# SolaraSphere: Radio Atlas

[![Backend CI](https://github.com/solaranoir/radio-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/solaranoir/radio-atlas/actions/workflows/ci.yml)

> A beautiful, explainable, and interactive radio intelligence platform that transforms amateur radio into an explorable world.

*Observe. Explain. Predict. Replay. Explore.*

---

## Current Status

🌎 **v0.2.0 — Phase 2: Radio Weather Globe**

Phases 1 and 2 are complete. Historical replay and analytics are in development.

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
- Live great-circle signal paths, with strength derived from SNR
- Spot-density visualization
- Solar terminator visualization
- Solar-weather visualization
- Observation filtering synchronized with globe rendering
- Station and signal-path selection with information panels
- Layer visibility controls with persisted preferences
- Mouse and keyboard globe navigation
- Reduced-motion support
- Rendering performance monitoring
- Unit, end-to-end, and visual regression testing

### Current Release

**v0.2.0** establishes the Radio Weather Globe and completes the live
observation-to-visualization pipeline.

Production propagation predictions and AI-driven explanations remain planned
for later phases.

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

---

## Product Roadmap

Each phase adds capabilities to the same data and visualization platform.

| Phase | Status | Scope |
| --- | --- | --- |
| 1 — Foundation & Data Platform | ✅ Released as [v0.1.0](https://github.com/solaranoir/radio-atlas/releases/tag/v0.1.0) | Ingestion, normalization, persistence, APIs and development infrastructure ([tasks](Phase1_tasks.md)) |
| 2 — Radio Weather Globe | ✅ Released as [v0.2.0](https://github.com/solaranoir/radio-atlas/releases/tag/v0.2.0) | Interactive globe, visualization layers, filtering, live rendering and browser testing ([tasks](Phase2_tasks.md)) |
| Current | 🚧 In development | Historical replay, timeline controls, propagation analytics and anomaly detection |

### Planned

- **Explain:** evidence-grounded AI explanations and QSO story generation
- **Predict:** band forecasting, prediction paths and confidence scoring
- **Explore:** rare-contact intelligence and achievements
- **Platform:** expanded accessibility validation and production hardening

---

## Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, Zustand |
| Globe rendering | Three.js |
| Backend | FastAPI, Python 3.12+ |
| Data | PostgreSQL, Redis |
| Data sources | NOAA, PSK Reporter |
| Testing | Pytest, Vitest, React Testing Library, Playwright |
| Containers | Docker |

---

## Architecture

```text
NOAA, PSK Reporter
        │
        ▼
Providers and ingestion ──► Normalized domain models ──► PostgreSQL
                                                            │
                                                            ▼
                                                         FastAPI
                                                            │
                                                            ▼
React application: filtering, state, analysis, visualization adapters
        │
        ▼
Three.js renderer: stations, signal paths, spot density, solar terminator,
solar weather (planned: prediction paths, anomalies)
```

The renderer never retrieves API data. Application data is transformed into
renderer-facing visualization models before crossing the React-to-Three.js
boundary. See [Globe Architecture](docs/architecture/Globe_Architecture.md).

---

## Getting Started

Prerequisites: Git, Docker with Compose, and Node.js 24 with npm for frontend
work (see `.nvmrc`).

```bash
git clone git@github.com:solaranoir/radio-atlas.git
cd radio-atlas
cp .env.example .env          # review local settings
docker compose up --build     # stop with: docker compose down
```

| Service | Address |
| --- | --- |
| FastAPI | `http://localhost:8000` |
| OpenAPI documentation | `http://localhost:8000/docs` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

Start the frontend with `cd frontend && npm install && npm run dev`.

See [Local Development](docs/development/LOCAL_DEVELOPMENT.md) for resets,
logs, database shells and troubleshooting.

---

## Testing

| Suite | Command | Covers |
| --- | --- | --- |
| Backend | `docker compose exec api pytest` | Providers, normalization, domain models, repositories, analytics, replay |
| Frontend unit | `npm test` | State, filtering, visualization utilities, rendering layers, the React-to-Three.js boundary |
| Lint and build | `npm run lint`, `npm run build` | Frontend static checks and production build |
| End-to-end | `npm run test:e2e` | Layers, filters, selection and camera behavior in the browser |
| Visual regression | `npm run test:visual` | Deterministic baselines for the globe, signal paths, spot density and animation |

Frontend commands run from `frontend/`. Update visual baselines with
`npm run test:visual:update`, and only after confirming the rendered change is
expected.

---

## Repository Layout

| Path | Contents |
| --- | --- |
| `backend/` | FastAPI app, ingestion worker, migrations, tests and backend docs |
| `frontend/` | React app, Three.js globe, timeline, unit, end-to-end and visual tests |
| `docs/` | ADRs, architecture, deployment, development, research and UX docs |
| `plan_requirements/` | Product requirements and implementation plan |
| `research_papers/` | Reference papers |
| `.github/workflows/` | Continuous integration |
| `docker-compose*.yml` | Local stack and test harnesses |
| `render.yaml` | Render deployment Blueprint |

---

## Documentation

- **Product:** [requirements](plan_requirements/) and phase plans ([Phase 1](Phase1_tasks.md), [Phase 2](Phase2_tasks.md))
- **Decisions:** [Architecture Decision Records](docs/adr/README.md)
- **Architecture:** [globe](docs/architecture/Globe_Architecture.md), [layers](docs/architecture/Layer_Architecture.md), [components](docs/architecture/Component_Diagrams.md), [sequences](docs/architecture/Sequence_Diagrams.md), [Phase 2 review notes](docs/architecture/Phase_2_Review_Notes.md) and [backend](backend/docs/)
- **UX:** [animation specification](docs/ux/Animation_Specification.md) and [UX docs](docs/ux/)
- **Operations:** [local development](docs/development/LOCAL_DEVELOPMENT.md) and [Render deployment](docs/deployment/Render.md)

---

## Guiding Principles

- Provider abstraction
- Explicit domain boundaries
- Local-first personal data
- Evidence-grounded AI
- Domain-driven state management
- Event-based historical replay
- Semantic visualization
- Rendering isolated from API retrieval
- Accessibility as a system concern rather than a final polish step

Contributions follow the [coding standards](coding_standards.md).

---

## License

License selection is pending.
