# SolaraSphere: Radio Atlas
## Requirements Document 

# 2. Product Requirements Document (PRD)

## 2.1 Product Name

**SolaraSphere: Radio Atlas**

---

## 2.2 Product Description

Radio Atlas is an interactive radio weather observatory that transforms amateur radio activity into a living, explorable environment.

Unlike traditional amateur radio applications that focus on logging, spot aggregation, or station control, Radio Atlas emphasizes **observation, explanation, prediction, and exploration.**

The platform combines:

* Real time data ingestion
* Geospatial visualization
* Historical analysis
* Predictive analytics
* Artificial intelligence
* Temporal replay
* Scientific storytelling

Instead of presenting propagation as static measurements, Radio Atlas visualizes the ionosphere as a dynamic system.

Signals become pathways.

Propagation behaves like weather.

Contacts become stories.

The system should answer three fundamental questions:

* **What is happening right now?**
* **Why is it happening?**
* **What is likely to happen next?**

The platform will support:

* Desktop
* Tablet
* Mobile

---

## 2.3 Core Product Pillars

### Pillar 1: Observe

Users should be able to visualize and explore radio activity as a dynamic, living system.

The application should emphasize:

* Discovery
* Pattern recognition
* Spatial awareness
* Real time observation

---

### Pillar 2: Explain

The system should explain radio phenomena rather than simply displaying measurements.

AI should function as an evidence based explanation layer.

The application should prioritize:

* Propagation explanations
* Educational narratives
* Environmental context
* Explainable AI

---

### Pillar 3: Predict

The application should provide actionable forecasts rather than historical reporting alone.

Predictions should be derived from both observed data and propagation models.

---

### Pillar 4: Explore Through Time

The system should allow users to move backward and forward through propagation events.

Users should be able to observe how the radio environment changes over time.

---

### Pillar 5: Beautiful Scientific Visualization

The application should feel more like a digital planetarium or observatory than traditional amateur radio software.

The interface should be:

* Beautiful
* Functional
* Educational
* Memorable

---

## 2.4 Primary Features

### Feature 1: Radio Weather Globe

#### Description

An interactive three dimensional globe that visualizes propagation as a dynamic environmental system.

The globe is the primary user interface and the foundation of the entire application.

Unlike traditional dashboards, the globe should communicate radio conditions visually, allowing users to perceive changes in propagation within seconds.

---

#### User Story

> As an operator, I want to visualize radio activity on a global map so that I can immediately understand propagation conditions.

---

#### Functional Requirements

The system shall:

* Display an interactive 3D globe.
* Allow zooming and rotation.
* Render radio contacts as animated arcs.
* Display the Earth's day/night boundary.
* Update data continuously.
* Support multiple simultaneous visualization layers.
* Function as the primary navigation interface.

---

#### Filtering

The system shall allow filtering by:

* Band
* Mode
* Geographic region
* Callsign
* Time window
* DX entity
* Signal source

---

#### Radio Weather Layers

| Layer | Priority |
| --- | --- |
| Spot density | Required |
| Signal strength | Required |
| Gray line | Required |
| Solar terminator | Required |
| Historical propagation | Required |
| Predicted propagation | Required |
| Propagation anomalies | Required |
| Aurora | Optional |
| MUF | Optional |
| Personal QSOs | Optional |
| POTA | Future release |
| Satellite passes | Future release |

---

#### Radio Weather Visualization Behaviors

The globe shall support the following visual behaviors:

| Behavior | Visualization |
| --- | --- |
| Spot density | Geographic regions pulse |
| Signal strength | Paths brighten and dim |
| New openings | Pathways appear and dissolve |
| Day/night changes | Terminator sweeps across the globe |
| Historical replay | Conditions morph over time |
| Forecasts | Dashed, semi transparent paths |
| Anomalies | Brief visual flares |

---

### Feature 2: QSO Story and Contact Intelligence

#### Description

An evidence grounded AI system that explains why a contact occurred.

This feature transforms radio contacts into narrative experiences supported by measurable observations.

Rather than functioning as a chatbot, AI serves as an interpretive layer that sits on top of propagation data.

The feature should be presented as a contextual slide out panel that appears when users select a propagation path.

---

#### User Story

> As an operator, I want the software to explain why a contact occurred so that I can better understand propagation.

---

#### Functional Requirements

The system shall:

* Generate AI assisted narratives.
* Explain propagation conditions.
* Identify environmental influences.
* Analyze signal paths.
* Compare contacts against historical observations.
* Support multiple explanation levels.

---

#### Evidence Categories

The system shall present:

* Distance
* Path geometry
* Solar conditions
* Time of day
* Gray line overlap
* Signal reports
* Contact rarity
* Historical comparisons

---

#### AI Narrative Requirements

The application shall distinguish between:

* Observed data
* Modeled predictions
* AI interpretations

The system shall present evidence before displaying AI generated conclusions.

---

#### Contact Intelligence

The system shall identify:

* Rare grid squares
* Rare DX entities
* Unusual propagation paths
* Long distance contacts
* First time contacts
* Statistical outliers
* Low probability events

---

#### Achievement System

The system shall support:

* Longest Path
* Midnight DX
* Polar Crossing
* Gray Line Hunter
* Rare Grid Explorer
* Pacific Pathfinder
* New Continent

---

### Feature 3: Radio Forecast

#### Description

A forecasting engine that predicts short term propagation opportunities.

Forecasting should be based on both observed radio activity and propagation models.

The system should function as an analytical workspace rather than a simple prediction widget.

---

#### User Story

> As an operator, I want to know which bands are likely to open so that I can make better operating decisions.

---

#### Functional Requirements

The system shall:

* Forecast one to three hours into the future.
* Rank propagation opportunities.
* Display confidence scores.
* Visualize likely openings geographically.
* Support multiple forecasting providers.

---

#### Predictions Shall Include

* Band availability
* Geographic openings
* Propagation quality
* Signal strength
* Opening windows
* Closing windows

---

#### Inputs

* Solar flux
* K index
* Sunspot number
* Historical spot data
* Time of day
* Seasonal patterns
* Historical propagation models

---

#### Outputs

* Probability scores
* Ranked band recommendations
* Geographic recommendations
* Predicted DX opportunities
* Confidence intervals

---

#### Forecast Architecture

The forecasting engine shall support interchangeable providers.

Examples include:

* Observational models
* VOACAP
* Third party propagation models
* Experimental machine learning models

---

### Feature 4: Propagation Time Machine

#### Description

A historical replay engine that reconstructs and replays the radio environment.

Replay should function as a scientific visualization tool rather than a media player.

Users should be able to observe how propagation evolved over time.

---

#### User Story

> As an operator, I want to replay propagation events so that I can understand how conditions changed.

---

#### Functional Requirements

The system shall:

* Store historical activity.
* Reconstruct previous conditions.
* Synchronize all active data layers.
* Support interactive timeline navigation.

---

#### Replay Shall Include

* Signal activity
* Gray line movement
* Solar changes
* Spot density
* Band transitions
* Geographic openings
* Anomaly detection

---

#### Playback Controls

The user shall be able to:

* Play
* Pause
* Fast forward
* Rewind
* Change playback speed
* Scrub through the timeline
* Select a custom time window

---

### Feature 5: Anomaly Detection

#### Description

An analytics engine that identifies unusual propagation events in real time.

This feature applies quality engineering principles to propagation analysis by comparing expected behavior against observed behavior.

---

#### User Story

> As an operator, I want to know when something unusual is happening so that I can investigate potential opportunities.

---

#### Functional Requirements

The system shall identify:

* Unexpected band openings
* Unusual propagation paths
* Rapid signal changes
* Rare geographic paths
* Unexpected signal density
* Long path opportunities

---

#### Anomaly Detection Categories

| Event | Example |
| --- | --- |
| Unexpected opening | 10m activity exceeds expected baseline |
| Geographic anomaly | Unusual North America to Asia propagation |
| Temporal anomaly | Rapid changes in signal density |
| Solar anomaly | Unexpected behavior during disturbed conditions |
| Contact anomaly | Extremely rare contact path |

---

## 2.5 Minimum Viable Product (MVP)

### Phase 1: Observe

Required functionality:

* Interactive globe
* NOAA integration
* PSK Reporter integration
* Live signal arcs
* Spot density visualization
* Gray line visualization
* Terminator rendering

---

### Phase 2: Explain

Enhanced functionality:

* AI generated narratives
* Contact intelligence
* Rare contact detection
* Achievement generation

---

### Phase 3: Explore

Advanced functionality:

* Historical replay
* Timeline controls
* Propagation reconstruction
* Synchronized layer playback

---

### Phase 4: Predict

Future functionality:

* Forecasting engine
* Geographic predictions
* Multiple propagation providers
* Experimental machine learning models

---

## 2.6 Out of Scope (Version 1.0)

The following features are explicitly excluded from the initial release:

* Traditional logging software replacement
* Contest management
* Digital mode transmission
* Rig control
* SDR integration
* Electronic QSL management
* CW decoding
* Voice mode decoding
* Remote station control

These features may be considered in future releases.

---

## 2.7 Competitive Differentiators

Radio Atlas is intentionally **not** designed to compete directly with existing dashboard applications.

The project's primary differentiators are:

* Radio weather visualization
* Evidence grounded AI
* Historical propagation reconstruction
* Explainable forecasts
* Scientific storytelling
* Anomaly detection
* Observatory inspired user experience

The objective is to create an application that feels less like traditional amateur radio software and more like a digital observatory for the ionosphere.
