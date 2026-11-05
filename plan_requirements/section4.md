# 4. User Stories

---

# Epic 1: Radio Weather Visualization

---

## Story 1.1

**As an operator, I want to view a live Radio Weather Globe so that I can understand propagation conditions around the world.**

### Acceptance Criteria

* Globe loads in less than three seconds.
* Globe supports mouse and touch controls.
* Signal paths update automatically.
* Visualization remains smooth at 60 FPS.

---

## Story 1.2

**As an operator, I want regions of the globe to pulse according to signal activity so that I can identify propagation hotspots immediately.**

### Acceptance Criteria

* Spot density updates automatically.
* Visual changes are smooth.
* Density changes are clearly distinguishable.

---

## Story 1.3

**As an operator, I want to filter radio activity by band so that I can focus on my current operating conditions.**

### Acceptance Criteria

* Filters support all amateur bands.
* Changes are applied immediately.
* Multiple filters can be combined.

---

## Story 1.4

**As an operator, I want to view only my own contacts so that I can analyze my personal operating history.**

### Acceptance Criteria

* User contacts can be isolated.
* Filters can be saved.
* Preferences persist between sessions.

---

# Epic 2: Evidence Grounded Explanation

---

## Story 2.1

**As an operator, I want the application to explain why a contact occurred so that I can better understand propagation.**

### Acceptance Criteria

* AI explanations are generated automatically.
* Explanations reference observed data.
* Explanations include supporting evidence.

---

## Story 2.2

**As an operator, I want the application to distinguish between measured, modeled, and AI interpreted information so that I understand the source of every conclusion.**

### Acceptance Criteria

* Observed data is labeled.
* Predictions are labeled.
* AI interpretations are labeled.

---

## Story 2.3

**As an operator, I want gray line propagation to be highlighted so that I can identify favorable operating windows.**

### Acceptance Criteria

* Gray line updates in real time.
* The day/night terminator is displayed.
* Visual overlays can be enabled or disabled.

---

# Epic 3: Radio Forecast

---

## Story 3.1

**As an operator, I want to know which bands are likely to open during the next three hours so that I can plan my operating session.**

### Acceptance Criteria

* Forecasts are generated within five seconds.
* Predictions include confidence scores.
* Bands are ranked.

---

## Story 3.2

**As a DX operator, I want the system to identify likely geographic openings so that I can pursue rare contacts.**

### Acceptance Criteria

* Geographic opportunities are highlighted.
* Opportunities are ranked.
* Confidence intervals are displayed.

---

# Epic 4: Propagation Time Machine

---

## Story 4.1

**As an operator, I want to replay propagation events so that I can understand how conditions evolved over time.**

### Acceptance Criteria

* Timeline controls are available.
* Playback supports multiple speeds.
* Users can pause and resume playback.

---

## Story 4.2

**As an educator, I want to replay historical propagation during demonstrations so that students can visualize radio concepts.**

### Acceptance Criteria

* Historical data is preserved.
* Playback supports full-screen presentation mode.
* Playback remains smooth during animation.

---

## Story 4.3

**As an observer, I want historical conditions to morph continuously during replay so that I can perceive how the ionosphere changes.**

### Acceptance Criteria

* Active layers remain synchronized.
* Historical transitions are animated.
* Replay preserves temporal accuracy.

---

# Epic 5: Contact Intelligence and Anomaly Detection

---

## Story 5.1

**As an operator, I want the application to identify unusual contacts so that I can discover interesting patterns in my operating history.**

### Acceptance Criteria

* Rare contacts are identified automatically.
* Long-distance contacts are highlighted.
* Rare paths are categorized.

---

## Story 5.2

**As an operator, I want the system to identify propagation anomalies so that I can investigate unexpected opportunities.**

### Acceptance Criteria

* Anomalies are detected automatically.
* Significant events are highlighted visually.
* Anomalies include supporting evidence.

---

## Story 5.3

**As an award hunter, I want to earn achievements based on my operating activity so that I can track progress and remain engaged.**

### Acceptance Criteria

* Achievements are generated automatically.
* Badges are stored.
* Achievement criteria are documented.

---

# Epic 6: Observatory Mode

---

## Story 6.1

**As an operator, I want to enter a passive observation mode so that I can simply watch the radio environment evolve.**

### Acceptance Criteria

* The interface supports a presentation mode.
* Visual elements continue updating automatically.
* The globe can be observed without user interaction.

---

## Story 6.2

**As an educator, I want AI generated observational captions to appear during demonstrations so that students understand what they are seeing.**

### Acceptance Criteria

* Captions are optional.
* Captions are based on observed data.
* Captions update automatically.

---

# Epic 7: Portfolio Demonstration

---

## Story 7.1

**As a hiring manager, I want to review the architecture and implementation so that I can evaluate engineering skills.**

### Acceptance Criteria

* Documentation is complete.
* Architecture diagrams are available.
* Source code is organized.

---

## Story 7.2

**As a reviewer, I want to see evidence of modern AI engineering practices so that I can evaluate the implementation critically.**

### Acceptance Criteria

* AI integrations are documented.
* Prompting strategies are documented.
* AI explainability is documented.
* AI generated features are clearly identified.

---

# Future User Stories

The product backlog should eventually include:

* Satellite overlays
* POTA overlays
* SOTA activations
* EME operations
* Contesting
* SDR integration
* Voice mode analysis (see Backlog Story B.1: SSB Spot Ingestion)
* Machine learning experimentation
* Club collaboration
* Social sharing
* Team operating
* Progressive web app support
* Wearable device integration

These stories should remain in the backlog until after Version 1.0 is complete.

---

## Backlog Story B.1: SSB Spot Ingestion

**As an operator, I want SSB (voice) activity included in Radio Atlas so that I can see phone-mode propagation, not only digital and CW modes.**

### Context

All spot data currently comes from PSK Reporter, which only receives reports that software decodes automatically: FT8, FT4, WSPR, JS8, CW (from automated skimmers) and similar modes. Voice cannot be decoded automatically, so PSK Reporter has essentially no SSB reports. A 2-minute sample of the full feed on 2026-11-05 (about 219 spots/s) contained none.

SSB activity is mainly available from the DX cluster network (telnet/web clusters), where operators post spots by hand. Those spots differ from PSK Reporter reports:

* They are posted by hand and sparse: one spot per notable station, not one per decode.
* They carry no signal-to-noise measurement. Free-text comments may include a signal report.
* They over-represent rare stations, DXpeditions and contest activity, so they show where people are interested, not the full propagation picture.
* The spotter's location is often coarse or missing.

### Acceptance Criteria

* A DX cluster provider is implemented behind the existing provider abstraction (ADR-003). It connects, authenticates if required, reconnects, and is monitored like the PSK Reporter provider.
* Cluster spot lines are parsed into normalized spot observations: spotter, spotted station, frequency, derived band, mode, time and comment.
* Mode is assigned from frequency and band-plan segments when the cluster does not state it, and the result records whether the mode was declared or inferred.
* Spot locations are resolved from callsign prefix (DXCC entity) when no grid is available, and the precision of each location is recorded.
* Cluster spots are stored with their provider and source, so analytics, rollups and anomaly baselines can include or exclude them. They are not merged silently into PSK Reporter series.
* Duplicate spots for the same station and frequency within a short window are deduplicated.
* SSB activity can be toggled as its own layer or filter in the globe and timeline.
* The documentation states the sampling bias and the missing signal measurements, and anomaly detection does not treat cluster spot volume as comparable to PSK Reporter decode volume.

### Open Questions

* Which cluster sources to use (for example DX Spider or AR-Cluster nodes, or an aggregated web feed), and their terms of use and rate limits.
* Whether cluster CW, RTTY and digital spots are ingested too, or only SSB, to avoid overlapping with PSK Reporter.
* Retention and storage: expected volume is far below PSK Reporter's, but it should be measured before deciding.
* Whether a new ADR is needed for spots posted by hand versus decoded automatically.

### Dependencies

* ADR-003: Provider Abstraction
* Story 4.6 ingestion worker, and multi-topic and retention support (PR #86)
* Epic 5 anomaly detection: cluster spots must be kept out of PSK Reporter baselines or modeled separately
