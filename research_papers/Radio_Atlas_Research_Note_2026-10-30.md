# Radio Atlas / SolaraSphere Research Note
## October 30, 2026 Research Brief - Roadmap Additions

### Purpose

This note converts the October 30, 2026 research brief into concrete work items for the Radio Atlas / SolaraSphere roadmap. The emphasis is on work that strengthens the existing PyRayHF + PSK Reporter validation framework before adding more complex ML forecasting.

The central implementation theme is **spatially aware model evaluation**: observations should be associated with the actual propagation path, their provenance should remain visible, and residuals should be analyzed in the coordinate system and time horizon that best match the physical process being modeled.

---

## 1. Highest-priority roadmap addition: Spatially aware absorption validation

### Proposed backlog item
**Story 6.19 - Spatially Aware Absorption Validation**

### Research basis
Gillies et al. show that HF link reliability during absorption events depends strongly on how close the absorption measurement is to the actual HF propagation path. A riometer measurement can be physically valid yet poorly predictive of a particular link if it is geographically displaced from the relevant D-region pierce points.

### Problem statement
The current reachability-vs-detectability roadmap assumes that external absorption observations can be associated with a path. That association needs explicit spatial logic. A regional absorption measurement should not automatically be treated as representative of the entire HF path.

### Proposed work

1. Extend the propagation-path model to include estimated D-region pierce points for each predicted hop.
2. Add spatial metadata to absorption observations:
   - instrument location
   - measurement timestamp
   - absorption value and frequency
   - nearest path segment or pierce point
   - great-circle separation
   - association confidence
3. Implement an `AbsorptionAssociationService` that ranks candidate measurements by path relevance.
4. Compare dropout prediction using:
   - nearest measurement
   - regional average
   - distance-weighted measurements
   - no absorption input
5. Persist the association method and distance in each experiment result.
6. Evaluate whether path-aware absorption association improves precision/recall for observed signal dropouts.

### Suggested schema additions

```text
absorption_observation_id
absorption_db
absorption_frequency_mhz
instrument_lat
instrument_lon

nearest_pierce_point_lat
nearest_pierce_point_lon
path_separation_km
association_method
association_confidence
```

### Acceptance criteria

- Every absorption observation used in an experiment has explicit spatial provenance.
- The experiment can compare multiple association strategies using the same observation corpus.
- A report can show dropout prediction performance as a function of measurement-to-path distance.
- The model never treats a distant regional absorption observation as path-local without recording that assumption.

---

## 2. Ionospheric observation provenance and quality

### Proposed backlog item
**Story 6.20 - Ionospheric Observation Provenance and Quality Metadata**

### Research basis
The COSMIC-2 / FY-3 / Tianmu-1 intercomparison demonstrates that electron-density products from different radio-occultation missions can contain systematic biases and different validity characteristics even when measuring the same broad physical quantity.

### Proposed work

Create a source-aware observation model rather than ingesting electron-density products as interchangeable values.

```text
IonosphereObservation
  source
  mission
  retrieval_method
  timestamp
  latitude
  longitude
  altitude_range
  nmf2
  hmf2
  vtec
  quality_flags
  uncertainty
  source_version
```

### Implementation tasks

- Add source and retrieval metadata to the ionospheric observation schema.
- Preserve instrument/mission-specific quality flags.
- Store original units and conversion history.
- Prevent source provenance from being discarded during normalization.
- Add source-stratified evaluation metrics.
- Allow experiments to compare predictions against only one observation source at a time.

### Acceptance criteria

A model-evaluation run can answer:

> How does this propagation model perform when evaluated against COSMIC-2-derived state estimates versus FY-3-derived estimates?

without re-ingesting the source data.

---

## 3. Geomagnetic-coordinate features for spatial residual analysis

### Proposed backlog item
**Story 6.21 - Geomagnetic Spatial Features**

### Research basis
The SuperDARN/SECIRA irregularity study found magnetic local time and geomagnetic latitude especially useful for modeling high-latitude irregularity occurrence.

### Proposed work

Add derived spatial features to experiment records:

```text
geomagnetic_latitude
geomagnetic_longitude
magnetic_local_time
path_midpoint_mlat
path_midpoint_mlt
```

### Evaluation

Compare residual clustering in:

1. geographic coordinates;
2. geomagnetic coordinates;
3. local solar time;
4. magnetic local time.

This should initially be an evaluation feature, not an additional production prediction dependency.

### Acceptance criteria

Residual dashboards can group prediction errors by MLAT/MLT as well as geographic latitude/longitude.

---

## 4. Forecast-horizon-aware feature evaluation

### Proposed backlog item
**Story 6.22 - Forecast Horizon Feature Benchmark**

### Research basis
The irregularity-forecast study found that feature importance changes with prediction horizon. Some solar/geomagnetic variables were most useful for nowcasting, while others became more useful at longer lead times.

### Proposed work

Define explicit forecast horizons:

```text
nowcast       0-15 min
short_term    15 min-2 hr
medium_term   2-9 hr
```

For each horizon, benchmark feature groups:

- F10.7
- Kp / ap
- AE
- solar wind velocity
- IMF Bz
- solar-wind pressure
- local time
- geomagnetic coordinates

### Guardrail

Do not allow one feature-selection result to silently become the default for all forecast horizons.

---

## 5. Physics-guided residual learning research spike

### Proposed backlog item
**Research Spike 6.23 - Physics-Guided Residual Learning**

### Research basis
The October 27 physics-guided flow-matching paper reports improved TEC forecasting when a learned model is constrained by ionospheric dynamics rather than being trained as a purely statistical predictor.

### Proposed experiment

Do not replace IRI/PyRayHF.

Instead evaluate:

```text
IRI / ionospheric baseline
        |
        v
     PyRayHF
        |
        v
baseline path prediction
        |
        +---- environmental context
        |
        v
 residual correction model
```

### Initial research questions

- Can a learned residual model improve out-of-sample reachability predictions?
- Does a physics-consistency penalty improve performance during disturbed conditions?
- Does the learned correction generalize to transmitter/receiver pairs not seen during training?
- Are improvements in TEC prediction actually reflected in better HF path prediction?

### Evaluation guardrails

Use:

- chronological train/test splits;
- complete TX/RX-pair holdouts;
- storm-condition holdouts;
- baseline comparison against unchanged IRI/PyRayHF;
- calibration metrics, not only classification accuracy.

This should remain a research spike until the observation and residual datasets are mature enough to support defensible training.

---

## 6. External HF observation corpus evaluation

### Proposed backlog item
**Research Spike 6.24 - Evaluate IONIS-AI as an External Observation Corpus**

### Purpose

IONIS-AI exposes a large aggregated HF propagation dataset derived from WSPR, Reverse Beacon Network, contest, DXpedition, and PSK Reporter sources.

### Evaluation checklist

Before using it for model benchmarking:

- document the upstream source networks;
- inspect aggregation logic;
- confirm licensing and redistribution constraints;
- determine temporal and spatial resolution;
- inspect definitions of "signature" and "opening";
- identify duplicated observations across source networks;
- determine whether PSK Reporter data overlap with Radio Atlas's own evaluation corpus;
- establish train/test leakage controls.

### Recommended use

Use IONIS-AI first for exploratory analyses and long-term climatology checks, not as the authoritative ground-truth dataset.

Potential uses:

- band-opening climatology;
- path availability priors;
- seasonal patterns;
- candidate TX/RX pair selection;
- long-term comparison against Radio Atlas observations.

---

## 7. SolaraSignal follow-on: denoising robustness benchmark

### Proposed backlog item
**Story SS-?. Denoising and Robustness Benchmark**

### Research basis
The October 26 modulation-classification paper explores learned denoising as a defense against adversarial perturbations.

### Recommended scope

Treat this as a SolaraSignal experiment, not a Radio Atlas propagation task.

Compare:

1. raw IQ;
2. conventional filtering;
3. learned denoising;
4. classifier-only baseline.

Evaluate:

- clean accuracy;
- low-SNR accuracy;
- natural interference;
- fading;
- unseen signal conditions;
- inference cost;
- whether preprocessing removes weak but meaningful features.

The paper's adversarial results should not be assumed to transfer directly to naturally degraded HF signals.

---

# Recommended roadmap ordering

## P1 - Add now

1. **6.19 Spatially Aware Absorption Validation**
2. **6.20 Ionospheric Observation Provenance and Quality Metadata**

These directly strengthen the scientific validity of the existing PyRayHF / PSK Reporter framework.

## P2 - Add after the observation schema is stable

3. **6.21 Geomagnetic Spatial Features**
4. **6.22 Forecast Horizon Feature Benchmark**

These improve residual analysis and forecasting experiments without changing the core prediction engine.

## P3 - Research spikes

5. **6.23 Physics-Guided Residual Learning**
6. **6.24 IONIS-AI External Corpus Evaluation**

These should not become production dependencies until the baseline evaluation pipeline is reliable.

## SolaraSignal track

7. **Denoising and Robustness Benchmark**

Keep this work separate from the propagation-model backlog.

---

# Suggested experiment sequence

```text
PyRayHF path geometry
        |
        v
D-region pierce points
        |
        +---- nearby absorption observations
        |          |
        |          v
        |   spatial association
        |          |
        +----------+
        |
        v
reachability + detectability prediction
        |
        v
PSK Reporter / other HF observations
        |
        v
residuals
        |
        +---- geographic analysis
        +---- geomagnetic analysis
        +---- source-quality analysis
        +---- forecast-horizon analysis
        |
        v
future residual-learning experiments
```

---

# Research folder recommendations

Suggested layout:

```text
research/
  hf-propagation/
  ionosphere-modeling/
  model-evaluation/
  datasets-tools/
  signal-classification/
```

## Add to `research/hf-propagation/`

### Gillies et al. (2026)
**The Reliability of HF Propagation Links Over Canada During Absorption Events**  
DOI: https://doi.org/10.1029/2025SW004906

**Why keep it:** Direct empirical evidence linking D-region absorption, path geometry, frequency, and HF link reliability. This is a core reference for Story 6.19 and the reachability-vs-detectability architecture.

**Suggested filename:**  
`2026-gillies-hf-link-reliability-absorption-events.md`

---

## Add to `research/ionosphere-modeling/`

### Zhang et al. (2026)
**Validation and Intercomparison of Ionospheric Electron Density Products From COSMIC-2, FY-3, and Tianmu-1 Radio Occultation Missions**  
DOI: https://doi.org/10.1029/2025JA034975

**Why keep it:** Strong reference for multi-source electron-density data quality, systematic bias, and provenance requirements.

**Suggested filename:**  
`2026-zhang-radio-occultation-electron-density-validation.md`

### Yang et al. (2026)
**Physics-Guided Flow Matching: A Generative AI Framework for Global Total Electron Content Forecasting**  
arXiv: https://arxiv.org/abs/2610.37159

**Why keep it:** Useful architectural reference for physics-guided ML and residual-learning experiments. Keep it in the active research set, but mark its TIEGCM-only evaluation as a limitation.

**Suggested filename:**  
`2026-yang-physics-guided-flow-matching-tec.md`

---

## Add to `research/model-evaluation/`

### Berngardt & Lavygin (2026)
**Space Weather Dependence of Decameter-Scale Ionospheric Irregularities Spatial Distribution**  
arXiv: https://arxiv.org/abs/2610.29630

**Why keep it:** Supports MLAT/MLT-based residual analysis, feature-horizon evaluation, and high-latitude spatial modeling.

**Suggested filename:**  
`2026-berngardt-lavygin-ionospheric-irregularity-forecasting.md`

---

## Add to `research/datasets-tools/`

### IONIS-AI / ionis-mcp
Repository: https://github.com/qso-graph/ionis-mcp

**Why keep it:** Potential external corpus for long-term propagation analysis and path-selection experiments. Treat it as a dataset/tool reference, not a peer-reviewed source.

**Suggested filename:**  
`ionis-ai-hf-propagation-dataset-notes.md`

The research note should record provenance, aggregation assumptions, licensing, overlap with PSK Reporter, and data-leakage risks before the dataset is used in model evaluation.

---

## Add to `research/signal-classification/`

### Liu et al. (2026)
**A JiT-Based Denoising Defense Method Against Adversarial Examples for Radio Signal Automatic Modulation Classification**  
arXiv: https://arxiv.org/abs/2610.35084

**Why keep it:** Useful for SolaraSignal robustness experiments and learned preprocessing research. It is not a core propagation reference.

**Suggested filename:**  
`2026-liu-jit-denoising-automatic-modulation-classification.md`

---

# Priority for the research folder

If only three items are added immediately, use:

1. **Gillies et al. - HF link reliability during absorption events**
2. **Zhang et al. - electron-density product intercomparison**
3. **Yang et al. - physics-guided TEC forecasting**

These three map most directly to the current Radio Atlas architecture:

```text
measurement quality
        +
path-specific propagation physics
        +
future model correction
```

Berngardt & Lavygin should follow closely because it informs spatial and forecast-horizon evaluation.

IONIS-AI belongs in the repository as a dataset/tool note after provenance and leakage checks.

The JiT denoising paper belongs in the SolaraSignal branch rather than the core propagation research collection.

---

## October 30 research decision

The immediate roadmap should **not** prioritize another prediction model.

The higher-value work is to make the existing experiment scientifically harder to fool:

- associate observations with the actual propagation corridor;
- preserve data-source provenance and uncertainty;
- analyze residuals in physically meaningful coordinate systems;
- keep forecasting horizons explicit;
- only then evaluate learned corrections.

That sequencing gives future SolaraSphere models a much stronger benchmark to beat.
