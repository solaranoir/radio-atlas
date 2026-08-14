# SolaraSphere: Radio Atlas
## Requirements Document (Version 0.2)

# 1. Executive Summary

## 1.1 Project Overview

**SolaraSphere: Radio Atlas** is a modern, visually immersive amateur radio intelligence platform that transforms traditional radio data into an interactive, exploratory experience.

Most existing amateur radio applications present information as static tables, aging desktop interfaces, and disconnected utilities. Operators often rely on multiple applications to monitor propagation, view solar conditions, analyze contacts, track activations, and understand why a particular communication path succeeded.

Radio Atlas reimagines amateur radio software as a unified exploration platform.

Instead of presenting radio activity as lists of frequencies and signal reports, Radio Atlas visualizes the radio spectrum as a living environment.

* Propagation behaves like weather.
* Signals become animated pathways.
* Contacts become stories.
* Space weather becomes an explorable layer rather than a collection of numerical indices.

The application combines:

* Data visualization
* Real time mapping
* Predictive analytics
* Artificial intelligence
* Interactive exploration

The result is software that is both technically sophisticated and immediately understandable.

---

## 1.2 Vision Statement

> To create the most beautiful, functional, and informative visualization platform in amateur radio by transforming invisible radio activity into an explorable digital atlas.

---

## 1.3 Product Mission

Radio Atlas will help operators answer questions such as:

* Why am I hearing a particular station?
* Which band should I use right now?
* Why did propagation suddenly change?
* Which regions of the world are currently accessible?
* Which contacts are unusual or noteworthy?
* What will propagation look like in the next hour?

The platform will convert complex radio science into intuitive visual experiences.

---

## 1.4 Problem Statement

Current amateur radio software suffers from several limitations.

### Fragmented Workflows

Operators commonly switch between:

* Logging software
* PSK Reporter
* Solar data websites
* DX cluster applications
* POTA applications
* Satellite tracking software
* Band condition websites

No single application presents these data sources as a unified experience.

### Poor Visualization

Many applications rely on:

* Static tables
* Text heavy interfaces
* Legacy desktop layouts
* Minimal interactivity

This creates a steep learning curve for new operators and limits exploratory analysis.

### Limited Context

Traditional software answers:

> "What happened?"

Very little software answers:

> "Why did it happen?"

Most applications present raw data without providing contextual explanations.

---

## 1.5 Product Objectives

### Objective 1

Create an interactive visualization platform that makes propagation patterns immediately understandable.

### Objective 2

Demonstrate the practical application of artificial intelligence in amateur radio.

### Objective 3

Unify multiple amateur radio data sources into a single interface.

### Objective 4

Develop a portfolio quality software project that demonstrates:

* Full stack engineering
* Data visualization
* API integration
* Machine learning
* AI assisted development
* QA methodology
* UI/UX design

---

## 1.6 Success Metrics

| Metric | Target |
| --- | --- |
| Initial application load | < 3 seconds |
| Globe rendering | 60 FPS |
| API response time | < 500 ms |
| Forecast generation | < 5 seconds |
| QSO narrative generation | < 3 seconds |
| Interactive map responsiveness | < 100 ms |
| User satisfaction | > 80% |

---

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
