# 5. Functional Requirements

---

# 5.1 System Overview

Radio Atlas shall function as a modern **radio weather observatory and propagation intelligence platform**.

The application shall combine:

* Real time data ingestion
* Geospatial visualization
* Temporal analysis
* Historical reconstruction
* Predictive analytics
* Artificial intelligence
* Evidence-based explanation
* Contact intelligence
* Anomaly detection

The system shall collect, process, analyze, reconstruct, predict, and visualize radio activity from multiple external data sources.

The system shall distinguish between three categories of information:

| Information Type | Description |
| --- | --- |
| Observed | Measured data collected from external sources |
| Modeled | Statistical or physics-based predictions |
| Interpreted | AI-generated explanations |

The system shall clearly identify the source of every piece of information presented to the user.

---

# 5.2 Data Ingestion Requirements

---

## FR-001: External Data Sources

The system shall ingest data from multiple external providers.

### Initial Data Sources

| Source | Priority |
| --- | --- |
| NOAA Space Weather | Required |
| PSK Reporter | Required |
| Historical contact data (ADIF) | Required |
| QRZ | Optional |
| POTA | Future release |
| N2YO | Future release |
| VOACAP | Experimental |
| Third-party propagation providers | Experimental |

---

## FR-002: Provider Abstraction

The system shall implement a provider abstraction layer.

External data sources shall be interchangeable.

The system shall not tightly couple application logic to any individual provider.

---

## FR-003: Automatic Data Refresh

The system shall automatically refresh external data.

| Data Type | Refresh Interval |
| --- | --- |
| Solar conditions | 5 minutes |
| Spot data | 1 minute |
| Forecast models | 15 minutes |
| Historical archives | Daily |
| User statistics | On demand |

---

## FR-004: Data Validation

The system shall validate incoming data.

Validation shall include:

* Duplicate detection
* Timestamp verification
* Coordinate validation
* Missing value detection
* Schema validation
* Response integrity verification

---

## FR-005: Data Normalization

The system shall normalize all incoming data into a standardized internal format.

Normalization shall include:

* Geographic coordinates
* Time zones
* Grid squares
* Callsigns
* Signal reports
* Propagation metrics

---

## FR-006: Data Persistence

The system shall store historical data for:

* Replay
* Forecasting
* AI explanations
* Contact analytics
* Anomaly detection

---

# 5.3 Radio Weather Globe Requirements

---

## FR-007: Interactive Globe

The system shall render an interactive three-dimensional globe.

The globe shall support:

* Rotation
* Zooming
* Panning
* Mouse interaction
* Touch interaction

---

## FR-008: Globe as the Primary Interface

The globe shall function as the application's primary navigation model.

Users shall interact with radio activity directly through the globe rather than through traditional menus and tables.

---

## FR-009: Visualization Layers

The system shall support multiple simultaneous layers.

### Required Layers

| Layer | Priority |
| --- | --- |
| Spot density | Required |
| Signal paths | Required |
| Gray line | Required |
| Solar terminator | Required |
| Historical propagation | Required |
| Predicted propagation | Required |
| Anomaly visualization | Required |

### Optional Layers

| Layer | Priority |
| --- | --- |
| Aurora | Optional |
| MUF | Optional |
| Personal QSOs | Optional |

### Future Layers

| Layer | Priority |
| --- | --- |
| POTA | Future |
| Satellite passes | Future |

---

## FR-010: Radio Weather Behaviors

The globe shall support dynamic visual behavior.

| Behavior | Visualization |
| --- | --- |
| Spot density | Geographic pulsing |
| Signal strength | Path brightening |
| Propagation openings | Emerging pathways |
| Propagation closures | Dissolving pathways |
| Day/night transitions | Terminator movement |
| Historical replay | Morphing conditions |
| Predictions | Dashed or translucent paths |
| Anomalies | Short-duration visual flares |

---

## FR-011: Filtering

Users shall be able to filter by:

* Band
* Mode
* Callsign
* DX entity
* Geographic region
* Grid square
* Distance
* Time window

---

# 5.4 QSO Story Requirements

---

## FR-012: Evidence-Based Explanations

The system shall generate explanations for selected contacts.

The system shall prioritize evidence before AI interpretation.

---

## FR-013: QSO Story Generation

The system shall generate narratives that explain:

* Why a contact occurred
* Which propagation mechanisms were involved
* Which environmental conditions contributed

---

## FR-014: Evidence Categories

Every QSO explanation shall include:

* Distance
* Great-circle path
* Time of day
* Solar conditions
* Gray line overlap
* Signal reports
* Historical comparisons
* Contact rarity

---

## FR-015: Explanation Levels

Users shall be able to select multiple explanation modes.

Supported modes shall include:

* Beginner
* Educational
* Technical

---

## FR-016: Similar Contact Analysis

The system shall identify and display similar historical contacts.

---

# 5.5 Radio Forecast Requirements

---

## FR-017: Forecast Generation

The system shall generate short-term propagation forecasts.

The forecasting horizon shall be between one and three hours.

---

## FR-018: Forecast Outputs

Forecasts shall include:

* Band availability
* Geographic openings
* Signal quality
* Opening windows
* Closing windows
* Probability scores
* Confidence intervals

---

## FR-019: Forecast Inputs

Forecast calculations shall incorporate:

* Solar flux
* K index
* Sunspot number
* Historical observations
* Time of day
* Seasonal patterns

---

## FR-020: Forecast Provider Architecture

The forecasting engine shall support interchangeable models.

Supported providers may include:

* Observational models
* VOACAP
* Machine learning models
* Third-party propagation models

---

# 5.6 Propagation Time Machine Requirements

---

## FR-021: Historical Reconstruction

The system shall reconstruct previous propagation conditions.

---

## FR-022: Timeline Controls

The system shall support:

* Play
* Pause
* Rewind
* Fast forward
* Timeline scrubbing

---

## FR-023: Playback Speeds

The system shall support:

* 1x
* 2x
* 5x
* 10x

---

## FR-024: Historical Windows

The system shall support:

* Previous hour
* Previous 24 hours
* Previous week
* Custom date ranges

---

## FR-025: Synchronized Playback

All active layers shall remain synchronized during replay.

The following shall update simultaneously:

* Signal activity
* Gray line
* Spot density
* Solar conditions
* Forecast overlays
* Anomaly indicators

---

# 5.7 Contact Intelligence and Anomaly Detection

---

## FR-026: Rare Contact Identification

The system shall identify:

* Rare grid squares
* Rare DX entities
* Unusual propagation paths
* First-time contacts
* Long-distance contacts

---

## FR-027: Anomaly Detection

The system shall identify:

* Unexpected band openings
* Unusual geographic propagation
* Rapid signal changes
* Unexpected signal density
* Long-path opportunities

---

## FR-028: Achievement Generation

The system shall automatically generate achievements.

Supported achievements shall include:

* Longest Path
* Gray Line Hunter
* Midnight DX
* Rare Grid Explorer
* New Continent
* Pacific Pathfinder

---

# 5.8 User Data Requirements

---

## FR-029: Local-First Contact Analysis

The system shall support local ADIF import.

Contact analysis shall function without requiring cloud synchronization.

---

## FR-030: Optional User Accounts

User accounts shall be optional.

Users may choose to store data locally or synchronize it with a cloud profile.

---

## FR-031: User Preferences

Users shall be able to store:

* Callsigns
* Preferred bands
* Saved filters
* Layer preferences
* Visualization preferences

---

# 5.9 Observability Requirements

---

## FR-032: Application Monitoring

The system shall monitor:

* API health
* Ingestion health
* AI services
* Forecasting services
* Database performance

---

## FR-033: Structured Logging

The system shall log:

* API failures
* Data ingestion failures
* Forecasting failures
* AI failures
* User-facing errors

---
