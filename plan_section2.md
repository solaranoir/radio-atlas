# SolaraSphere: Radio Atlas
## Requirements Document 

# 2. Product Requirements Document (PRD)

## 2.1 Product Name

**SolaraSphere: Radio Atlas**

---

## 2.2 Product Description

Radio Atlas is a web based visualization platform that converts amateur radio contacts, propagation data, solar activity, and radio telemetry into an interactive exploration experience.

The application will combine:

* Real time data ingestion
* Predictive modeling
* Historical analysis
* Artificial intelligence

The system will support:

* Desktop
* Tablet
* Mobile

---

## 2.3 Core Product Pillars

### Pillar 1: Visual Exploration

Users should be able to discover patterns through interaction rather than manually analyzing data.

### Pillar 2: Contextual Intelligence

The system should explain radio phenomena rather than simply displaying measurements.

### Pillar 3: Predictive Insight

The application should provide actionable forecasts rather than historical reporting alone.

### Pillar 4: Delightful Design

The software should be aesthetically compelling and memorable.

---

## 2.4 Primary Features

# Feature 1: Propagation Globe

### Description

An interactive 3D globe displaying real time propagation and radio activity.

### User Story

> As an operator, I want to visualize radio activity on a global map so that I can understand propagation conditions at a glance.

### Functional Requirements

The system shall:

* Display an interactive 3D globe.
* Allow zooming and rotation.
* Render radio contacts as animated arcs.
* Display the Earth's day/night boundary.
* Support layer overlays.
* Update data automatically.

### Filtering

The system shall allow filtering by:

* Band
* Mode
* Geographic region
* Callsign
* Time window

### Propagation Layers

| Layer | Required |
| --- | --- |
| FT8 activity | Yes |
| PSK Reporter | Yes |
| Gray line | Yes |
| Solar terminator | Yes |
| Aurora | Yes |
| MUF | Yes |
| POTA | Yes |
| Satellite passes | Yes |
| Personal QSOs | Yes |
| DX entities | Yes |

---

# Feature 2: QSO Story Engine

### Description

An AI powered feature that transforms radio contacts into narrative explanations.

### User Story

> As an operator, I want the software to explain why a contact occurred so that I can better understand propagation.

### Functional Requirements

The system shall:

* Generate AI narratives for contacts.
* Explain propagation conditions.
* Identify environmental factors.
* Describe radio paths.

### Narratives shall include:

* Distance
* Solar conditions
* Band
* Time of day
* Gray line conditions
* Contact rarity

### Example Output

> At 7:42 PM, you contacted JA1ABC over 5,200 miles using 20 meters. The communication path crossed the gray line over the Pacific while the solar flux was 184. Similar contacts represented only 3% of your recent activity.

---

# Feature 3: Band Forecasting

### Description

A predictive analytics engine that forecasts likely propagation conditions.

### User Story

> As an operator, I want to know which bands are likely to open so that I can choose the most effective operating strategy.

### Functional Requirements

The system shall:

* Forecast 1 to 3 hours into the future.

### Predictions shall include:

* Band availability
* Geographic openings
* Propagation quality
* Expected signal strength

### Inputs

* Solar flux
* K index
* Sunspot number
* Historical spot data
* Time of day
* Seasonal patterns

### Outputs

* Probability scores
* Ranked band recommendations
* Predicted DX opportunities
* Opening and closing windows

---

# Feature 4: Propagation Replay

### Description

A historical playback engine that replays propagation activity over time.

### User Story

> As an operator, I want to replay previous propagation events so that I can understand how conditions evolved.

### Functional Requirements

The system shall:

* Store historical activity.
* Provide timeline controls.

### Replay shall include:

* Signal activity
* Gray line movement
* Solar changes
* Spot density
* Band transitions

### Playback Controls

The user shall be able to:

* Pause
* Play
* Fast forward
* Rewind
* Change playback speed
* Select a custom time window

---

# Feature 5: Rare Contact Discovery

### Description

An analytics engine that identifies unusual contacts and achievements.

### User Story

> As an operator, I want to discover exceptional contacts that I might otherwise overlook.

### Functional Requirements

The system shall identify:

* Rare grid squares
* Rare DX entities
* Unusual propagation paths
* Long distance contacts
* First time contacts
* Low probability events

### Achievement Badges

The system shall support:

* Longest Path
* Midnight DX
* Polar Crossing
* Gray Line Hunter
* New Continent
* Rare Grid Explorer

---

## 2.5 Minimum Viable Product (MVP)

### Phase 1

Required MVP functionality:

* Interactive globe
* NOAA integration
* PSK Reporter integration
* Gray line visualization
* Live signal arcs

### Phase 2

Enhanced functionality:

* AI generated narratives
* Historical replay
* Contact analytics

### Phase 3

Advanced functionality:

* Machine learning forecasting
* Satellite overlays
* POTA integration
* Achievement system

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

These features may be considered in future releases.
