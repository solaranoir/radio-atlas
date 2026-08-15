# SolaraSphere: Radio Atlas

# Repository README

> A beautiful, explainable, and interactive radio intelligence platform
> that transforms amateur radio into an explorable world.

------------------------------------------------------------------------

## Vision

Radio Atlas reimagines amateur radio software as a scientific
exploration platform rather than a collection of disconnected utilities,
aging desktop interfaces, spreadsheets, charts, and log windows.

Signals become animated pathways.

Propagation behaves like weather.

Contacts become stories.

Space weather becomes an explorable layer rather than a collection of
numerical indices.

The goal is to build the most beautiful, functional, and educational
visualization platform in amateur radio.

------------------------------------------------------------------------

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

------------------------------------------------------------------------

## Primary Features

### Radio Weather Globe

-   Live signal paths
-   Spot density
-   Gray-line visualization
-   Solar overlays
-   Animated propagation
-   Layer management

### QSO Story Engine

-   Evidence-based narratives
-   Propagation explanations
-   Historical comparisons
-   Educational explanations

### Band Forecasting

-   Opening probabilities
-   Geographic forecasts
-   Confidence scoring
-   Predicted propagation paths

### Historical Replay

-   Timeline controls
-   Time scrubbing
-   Propagation reconstruction
-   Historical exploration

### Rare Contact Discovery

-   Anomaly detection
-   Contact intelligence
-   Achievement generation
-   Statistical analysis

------------------------------------------------------------------------

## Technology Stack

  Layer              Technology
  ------------------ ---------------------
  Frontend           React 19
  Language           TypeScript
  Globe Rendering    Three.js
  Visualization      D3 + Deck.gl
  Backend            FastAPI
  Database           PostgreSQL
  Cache              Redis
  Background Tasks   Celery
  AI                 OpenAI
  Testing            Pytest + Playwright
  Containerization   Docker

------------------------------------------------------------------------

## Repository Structure

``` text
radio-atlas/

├── README.md
├── CODING_STANDARDS.md
├── CONTRIBUTING.md
├── ROADMAP.md
│
├── docs/
│   ├── requirements/
│   ├── architecture/
│   ├── adr/
│   ├── testing/
│   └── ux/
│
├── frontend/
│   └── src/
│       ├── app/
│       ├── globe/
│       ├── components/
│       └── services/
│
├── backend/
│   └── app/
│       ├── api/
│       ├── domain/
│       ├── providers/
│       ├── ingestion/
│       └── infrastructure/
│
├── tests/
├── scripts/
├── docker/
└── .github/

```

------------------------------------------------------------------------

## Documentation

  Document                        Purpose
  ------------------------------- -------------------------
  Product Requirements Document   Product definition
  Engineering Roadmap             Implementation plan
  Coding Standards                Development standards
  Architecture Decision Records   Architectural rationale
  System Architecture             Technical design
  Testing Strategy                Verification approach

------------------------------------------------------------------------

## Development Roadmap

1.  Foundation and architecture
2.  Data ingestion and APIs
3.  Radio Weather Globe
4.  Analytics and replay
5.  AI and forecasting
6.  Accessibility and deployment
7.  Portfolio packaging

------------------------------------------------------------------------

## Guiding Architectural Principles

-   Provider abstraction
-   Local-first personal data
-   Evidence-grounded AI
-   Domain-driven state management
-   Event-based historical replay
-   Semantic visualization

------------------------------------------------------------------------

## Development Standards

Every completed feature should include:

-   Types
-   Tests
-   Documentation
-   Error handling
-   Accessibility validation
-   Observability
-   Updated diagrams when necessary

------------------------------------------------------------------------

## License

License selection is pending.

------------------------------------------------------------------------

*Observe. Explain. Predict. Replay. Explore.*
# CI test
