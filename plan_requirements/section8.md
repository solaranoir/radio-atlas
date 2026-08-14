# 8. System Architecture

## 8.1 Architectural Principles

The architecture shall be based on the following principles:

- Modular design
- API-first development
- Provider abstraction
- Local-first personal data where practical
- Clear separation of observed, modeled, and interpreted data
- Service separation
- Independent deployments where useful
- Containerization
- Scalability
- Graceful degradation
- Testability
- Observability

The system should avoid unnecessary architectural complexity solely for portfolio appearance.

---

## 8.2 Architectural Pattern

The application shall use a layered, service-oriented architecture.

```text
                           User Interface
                                  │
                                  ▼
                         React / TypeScript
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
                 ▼                ▼                ▼
          Local Data Layer   Visualization     API Client
           (ADIF / Cache)       Engine             │
                                                   ▼
                                              FastAPI API
                                                   │
                  ┌────────────────────────────────┼────────────────────────┐
                  │                                │                        │
                  ▼                                ▼                        ▼
           Observation Services              AI Services          Forecast Services
                  │                                │                        │
                  ├───────────────┐                │                        │
                  ▼               ▼                ▼                        ▼
             Analytics       Replay Engine    Evidence Layer         Provider Layer
                  │               │                │                        │
                  └───────────────┴────────────────┼────────────────────────┘
                                                   ▼
                                           Storage / Cache
                                                   │
                                  ┌────────────────┴───────────────┐
                                  ▼                                ▼
                             PostgreSQL                          Redis
                                  │
                                  ▼
                         External Data Providers
```

---

## 8.3 Frontend Architecture
### Technology Stack

| Component | Technology |
| ----------------- | ------------ |
| Framework         | React 19     |
| Language          | TypeScript   |
| Styling           | Tailwind CSS |
| State management  | Zustand      |
| Routing           | React Router |
| Visualization     | D3           |
| Globe rendering   | Three.js     |
| Geospatial layers | Deck.gl      |
| Local storage     | IndexedDB    |


### ### Frontend Responsibilities

The frontend shall manage:

Globe rendering
Radio-weather animations
Layer composition
Timeline playback
Local ADIF analysis
Responsive layout
Accessibility behaviors
Local user preferences

### Frontend Modules
```text
frontend/

├── app/
├── components/
├── globe/
│   ├── layers/
│   ├── animations/
│   ├── interactions/
│   └── rendering/
├── forecast/
├── replay/
├── qso-story/
├── anomalies/
├── contacts/
├── local-data/
├── services/
├── hooks/
├── stores/
├── layouts/
└── utilities/
```

---

## 8.4 Backend Architecture

### Technology Stack

| Component | Technology |
| --------------- | ---------------------------------- |
| API             | FastAPI                            |
| Language        | Python                             |
| Database        | PostgreSQL                         |
| Cache           | Redis                              |
| Background jobs | Celery or equivalent               |
| ORM             | SQLAlchemy                         |
| AI integration  | OpenAI API or provider abstraction |
| Authentication  | JWT/OAuth as needed                |



### ### Backend Responsibilities

The backend shall manage:

External data ingestion
Normalization
Historical storage
Propagation analytics
Anomaly detection
Forecast orchestration
AI context generation
Evidence assembly
Optional cloud synchronization

### Backend Modules
```text
backend/

├── api/
├── domain/
├── ingestion/
├── providers/
├── observations/
├── replay/
├── forecasting/
├── anomalies/
├── ai/
├── evidence/
├── repositories/
├── models/
├── authentication/
└── utilities/
```

---

## 8.5 External Provider Architecture

### Initial Providers

```text
NOAA Space Weather ──────┐
PSK Reporter ────────────┤
                         ▼
                  Provider Adapters
                         │
                         ▼
                   Validation Layer
                         │
                         ▼
                  Normalization Layer
                         │
                         ▼
                Observation Repository
```
Future or optional providers may include:

VOACAP
QRZ
Additional propagation models
WSPR datasets
Reverse Beacon Network
POTA
N2YO

### Provider Abstraction

External providers shall be accessed through internal interfaces.

Example:
```text
ObservationProvider
├── PSKReporterProvider
├── WSPRProvider
└── RBNProvider

ForecastProvider
├── ObservedTrendProvider
├── VOACAPProvider
├── ThirdPartyModelProvider
└── ExperimentalMLProvider
```
The application shall not depend on a single forecasting or observation provider.

---

## 8.6 Data Ingestion Pipeline

```text
External Provider
        │
        ▼
Provider Adapter
        │
        ▼
Schema Validation
        │
        ▼
Normalization
        │
        ▼
Deduplication
        │
        ▼
Observation Storage
        │
        ├──────────────► Redis / Live Cache
        │
        ├──────────────► Historical Replay
        │
        ├──────────────► Analytics
        │
        └──────────────► Anomaly Detection
```

## 8.7 Local-First Personal Data Architecture

Personal log analysis shall support local-first processing.

```text
ADIF File
    │
    ▼
Browser Parser
    │
    ▼
IndexedDB
    │
    ├────────► Personal QSO Layers
    ├────────► Contact Intelligence
    └────────► QSO Story Context
```
Cloud synchronization shall be optional.

This architecture reduces:

Privacy risk
Infrastructure requirements
Unnecessary server-side storage

---

## 8.8 Database Architecture

### Primary Tables

```
| Table              | Purpose                                  |
| ------------------ | ---------------------------------------- |
| observations       | Normalized radio observations            |
| stations           | Callsign and station metadata            |
| solar_conditions   | Space-weather observations               |
| propagation_events | Detected openings or significant changes |
| anomalies          | Detected abnormal conditions             |
| forecasts          | Stored propagation forecasts             |
| forecast_providers | Forecast source metadata                 |
| narratives         | AI-generated explanations                |
| narrative_evidence | Evidence supporting explanations         |
| achievements       | Achievement definitions                  |
| user_achievements  | Optional synchronized achievements       |
| users              | Optional account records                 |

```
Personal QSOs may remain local and do not require server persistence by default.

---

## 8.9 AI Architecture

AI shall operate as an interpretation layer, not as a source of scientific truth.

### AI Pipeline
```text
Selected Contact / Event
          │
          ▼
     Context Builder
          │
          ├── Observed Data
          ├── Historical Comparison
          ├── Forecast Data
          └── Propagation Metrics
          │
          ▼
      Evidence Bundle
          │
          ▼
      Prompt Template
          │
          ▼
        LLM API
          │
          ▼
   Response Validation
          │
          ▼
    Labeled Narrative
          │
          ▼
       User Interface
```
AI Responsibilities

The AI system may support:

QSO Story generation
Propagation explanations
Educational explanations
Observational captions
Summary of anomaly evidence

AI shall not be responsible for:

Authentication
Data persistence
Globe rendering
Raw forecast calculation
Scientific measurements
Determining whether an observation actually occurred

---

## 8.10 Forecast Architecture

Forecasting shall use a provider abstraction rather than a single built-in model.

```text
Forecast Request
       │
       ▼
Forecast Orchestrator
       │
       ├── Observed Trend Provider
       ├── VOACAP Provider
       ├── Third-Party Model
       └── Experimental Model
       │
       ▼
Normalization
       │
       ▼
Confidence Scoring
       │
       ▼
Radio Forecast UI
```
The architecture should allow future model comparison and evaluation.

---

## 8.11 Replay Architecture

Historical replay shall use time-indexed observations.
```text
Replay Request
      │
      ▼
Time Window Query
      │
      ▼
Historical Observation Store
      │
      ▼
Replay Frame Builder
      │
      ├── Spots
      ├── Solar Conditions
      ├── Terminator
      ├── Anomalies
      └── Forecast Context
      │
      ▼
Synchronized Globe State
```

---

## 8.12 Anomaly Detection Architecture

```text
Live Observation Stream
          │
          ▼
Rolling Baseline
          │
          ▼
Statistical Comparison
          │
          ▼
Anomaly Detector
          │
          ├── Unexpected Density
          ├── Unexpected Path
          ├── Rapid Signal Change
          └── Geographic Outlier
          │
          ▼
Evidence Record
          │
          ▼
Globe Flare + Detail Panel
```

---

## 8.13 Deployment Architecture

### Development Environment
```text
React
FastAPI
PostgreSQL
Redis
Docker Compose
```
### Production Environment
```text
Browser
   │
   ▼
CDN
   │
   ▼
Frontend Application
   │
   ▼
API Gateway / Reverse Proxy
   │
   ▼
FastAPI Services
   │
   ├────────► Redis
   │
   └────────► PostgreSQL
          │
          ▼
Background Workers
          │
          ▼
External Providers
```
The architecture should remain deployable on modest infrastructure for portfolio and demonstration use.

---

## 8.14 Observability

The application shall implement:

- Structured logging
- Error tracking
- Performance monitoring
- API monitoring
- External provider health monitoring
- Database monitoring
- Forecast provider monitoring
- AI latency and failure monitoring
- Replay performance monitoring

---

## 8.15 Architecture Documentation Deliverables

The repository shall include:

- System context diagram
- Container diagram
- Component diagrams
- Sequence diagrams
- Data flow diagrams
- Entity relationship diagram
- Provider abstraction diagrams
- AI architecture diagram
- Replay architecture diagram
- Forecast architecture diagram
- Deployment diagram
- Architecture Decision Records (ADRs)

### Suggested ADRs

- Globe rendering technology selection
- Local first versus cloud QSO storage
- Propagation provider abstraction
- AI evidence grounding strategy
- Historical replay storage strategy
- Anomaly detection approach

These artifacts shall be maintained alongside the source code and updated as implementation decisions evolve.
