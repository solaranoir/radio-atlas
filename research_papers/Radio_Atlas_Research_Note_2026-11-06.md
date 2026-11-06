# Radio Atlas / SolaraSphere Research Note
## November 6, 2026 Research Brief - Roadmap Additions

### Purpose

This note converts the November 6, 2026 Radio Atlas / SolaraSphere research brief into concrete roadmap additions and research-library recommendations.

The strongest theme in this brief is **independent validation**. Radio Atlas should not rely on PSK Reporter reception outcomes alone when evaluating HF propagation models. Independent MUF observations, direct HF beacon measurements, uncertainty-aware ionospheric forecasts, and model-surrogate benchmarks can make the evaluation framework more scientifically robust.

---

# 1. Add independent MUF observations to the evaluation framework

## Proposed backlog item
**Story 6.25 - Independent MUF Observation Validation**

### Research basis

Hu et al. (2026) estimate maximum usable frequency from low-latitude long-range ionospheric radar observations by fitting ground/sea-scatter geometry against frequency. Their results show that real-time radar-derived MUF estimates can capture low-latitude spatial asymmetries and diurnal structure that may not be well represented by empirical models or isolated ionosonde observations.

### Problem statement

The current PyRayHF + PSK Reporter experiment evaluates whether modeled paths correspond to observed receptions. That is valuable, but a missing reception report is ambiguous.

A receiver may have been:

- offline,
- listening elsewhere,
- unable to decode the mode,
- below detection threshold,
- affected by local noise,
- or simply not reporting.

An independent MUF observation provides a more direct physical test of whether the modeled ionosphere supports a given path and frequency.

### Proposed work

1. Define a source-independent `MUFObservation` domain model.
2. Preserve:
   - observation time,
   - geographic region or path,
   - estimated MUF,
   - measurement method,
   - source,
   - spatial uncertainty,
   - temporal uncertainty,
   - quality flags.
3. Add a comparison layer between:
   - PyRayHF-derived MUF,
   - independent observed MUF,
   - PSK Reporter reception outcomes.
4. Evaluate:
   - absolute MUF error in MHz,
   - band-classification accuracy,
   - error by local time,
   - error by geomagnetic condition,
   - error by path distance.
5. Keep MUF evaluation metrics separate from reception/detectability metrics.

### Suggested schema

```text
MUFObservation
  timestamp
  source
  method
  tx_region
  rx_region
  midpoint_lat
  midpoint_lon
  muf_mhz
  uncertainty_mhz
  quality_flags
  source_version
```

### Acceptance criteria

- Radio Atlas can compare one modeled MUF value against one or more observed MUF measurements.
- Evaluation reports distinguish MUF prediction error from reception prediction error.
- Source provenance and uncertainty are preserved.
- Missing PSK Reporter reception never substitutes for a measured MUF observation.

---

# 2. Add an HF channel-characterization observation model

## Proposed backlog item
**Story 6.26 - HF Channel Characterization Observations**

### Research basis

Aricoche, Hysell, and Morton (2026) use an Alaskan HF beacon network to measure group delay, Doppler shift, amplitude, Doppler spreading, and range spreading at one-minute cadence. Their work demonstrates that an HF path contains much richer information than a simple reachable/not-reachable label.

### Problem statement

The current Radio Atlas experiment architecture is primarily binary:

```text
predicted_reachable
observed_reception
```

That is useful for the MVP, but it hides channel behavior that may explain why a geometrically valid path is difficult or impossible to use.

### Proposed work

Create an optional observational model for channel-state measurements.

```text
HFChannelObservation
  timestamp
  tx_id
  rx_id
  frequency_hz
  amplitude
  group_delay_ms
  doppler_shift_hz
  doppler_spread_hz
  delay_spread_ms
  snr_db
  source
  quality_flags
```

### Initial implementation tasks

- Add nullable channel-characterization fields to the experiment model.
- Do not require them for ordinary PSK Reporter observations.
- Keep direct beacon/radar measurements separate from inferred values.
- Support residual analysis between modeled path geometry and measured group delay.
- Add future hooks for Doppler-spread and delay-spread prediction.

### Acceptance criteria

Radio Atlas can ingest a channel-characterization observation without forcing it into a binary reception schema.

---

# 3. Benchmark a physics-informed ray-tracing surrogate

## Proposed backlog item
**Research Spike 6.27 - Physics-Informed Ray-Trajectory Surrogate**

### Research basis

Li et al. (2026) propose a physics-informed neural network for HF ionospheric ray-trajectory prediction. The model embeds Haselgrove-equation constraints into training and predicts ray trajectories without requiring electron-density forecasts as model input.

The reported trajectory RMSEs are 15.92 km on spatial test data and 7.54 km on temporal test data, with improvements over the conventional neural-network baselines used in the paper.

### Important limitation

The model is evaluated against conventional ray-tracing trajectories, not against independently observed HF paths.

This means it should be treated as a **surrogate-model candidate**, not evidence that it predicts the real ionosphere better than PyRayHF.

### Proposed experiment

Benchmark:

```text
PyRayHF
vs
PINN surrogate
```

using identical test paths.

Measure:

- trajectory RMSE,
- ground intercept error,
- apex-height error,
- hop-count agreement,
- takeoff-angle error,
- runtime,
- memory use,
- batch throughput,
- behavior on unseen paths,
- behavior on disturbed conditions.

### Decision rule

Only pursue a surrogate further if it provides a meaningful computational advantage without unacceptable loss of physical fidelity.

### Acceptance criteria

Produce a benchmark report answering:

> Is a physics-informed surrogate materially faster than PyRayHF at a level of error acceptable for Radio Atlas experiments?

---

# 4. Add uncertainty calibration to ionospheric forecasting

## Proposed backlog item
**Story 6.28 - Forecast Uncertainty Calibration**

### Research basis

Alford-Lago et al. (2026) forecast foF2, hmF2, and TEC using transformer-based models that combine historical observations, solar/geomagnetic drivers, and climatological predictions. Importantly, the model produces nonparametric uncertainty bounds.

### Problem statement

A point prediction such as:

```text
foF2 = 7.1 MHz
```

does not communicate whether the model is highly confident or operating far outside familiar conditions.

For a forecasting platform, uncertainty quality matters almost as much as prediction error.

### Proposed work

Add forecast-interval evaluation to SolaraSphere.

Evaluate:

- prediction interval coverage,
- average interval width,
- calibration by forecast horizon,
- calibration during storms,
- calibration by latitude,
- calibration for unseen geographic locations.

### Suggested metrics

```text
coverage_probability
mean_interval_width
coverage_error
sharpness
calibration_by_horizon
calibration_by_geomagnetic_state
```

### Acceptance criteria

A forecast model cannot be considered improved solely because its RMSE decreases. Its uncertainty intervals must also be evaluated for empirical coverage.

---

# 5. Investigate automated ionogram-layer extraction

## Proposed backlog item
**Research Spike 6.29 - Ionogram Layer Extraction Feasibility**

### Research basis

Sherstyukov et al. (2026) use an attention-based U-Net trained with synthetic ground truth to identify E, F1, and F2 traces in ionograms. The method generalizes to complex F-spread conditions and achieves small errors in extracted frequency and virtual-height parameters on an independent dataset.

### Recommended scope

Do not immediately build an image-processing pipeline.

First determine whether structured GIRO or ionosonde products already provide sufficient parameters for Radio Atlas.

If not, evaluate an isolated image-processing experiment.

### Questions to answer

- Are existing structured ionosonde products sufficient for:
  - foF2,
  - hmF2,
  - virtual heights,
  - spread-F flags,
  - layer quality?
- Are raw ionograms available with reliable metadata?
- Would pixel-level segmentation add information not already available in structured products?
- Is the expected benefit large enough to justify maintaining a vision model?

### Acceptance criteria

Produce a go/no-go note identifying whether custom ionogram image processing provides material value to Radio Atlas.

---

# 6. Strengthen the evaluation hierarchy

## Proposed architectural update

The November 6 brief suggests a clearer hierarchy of validation targets.

### Level 1 - Physical state

```text
foF2
hmF2
TEC
electron-density profile
```

### Level 2 - Propagation geometry

```text
MUF
ray trajectory
ground range
apex height
group delay
```

### Level 3 - Channel behavior

```text
Doppler shift
Doppler spread
delay spread
absorption
field strength
```

### Level 4 - Receiver outcome

```text
reported reception
SNR
decode success
```

A model can succeed at one level and fail at another.

For example:

```text
correct MUF
+
incorrect absorption estimate
=
valid path but failed reception prediction
```

This hierarchy should become explicit in experiment reports.

---

# Recommended roadmap ordering

## P1 - Add now

1. **6.25 Independent MUF Observation Validation**
2. **6.26 HF Channel Characterization Observations**

These directly improve the validity of the existing experiment framework.

## P2 - Add after observation interfaces stabilize

3. **6.28 Forecast Uncertainty Calibration**
4. **6.29 Ionogram Layer Extraction Feasibility**

## Research spike

5. **6.27 Physics-Informed Ray-Trajectory Surrogate**

This should remain isolated until PyRayHF performance becomes an actual bottleneck.

---

# Suggested experiment sequence

```text
Ionospheric state
      |
      v
   PyRayHF
      |
      +----------------------+
      |                      |
      v                      v
Predicted MUF         Predicted path geometry
      |                      |
      v                      v
Observed MUF          Beacon / channel observations
      |                      |
      +----------+-----------+
                 |
                 v
        Physical validation
                 |
                 v
        PSK Reporter outcome
                 |
                 v
      Detectability evaluation
```

This makes PSK Reporter one important observation layer rather than the only arbiter of whether the model was correct.

---

# Research folder recommendations

Suggested layout:

```text
research/
  hf-propagation/
  ionosphere-modeling/
  model-evaluation/
  signal-classification/
  datasets-tools/
```

## Add to `research/hf-propagation/`

### Li et al. (2026)
**A Novel Physics-Informed Neural Network for HF Ionospheric Ray Trajectory Prediction Without Electron Density Forecasts**

DOI: https://doi.org/10.1109/TAP.2026.3734213

**Why keep it:** Directly relevant to future PyRayHF surrogate modeling and physics-informed propagation ML.

**Suggested note filename:**
`2026-li-physics-informed-hf-ray-trajectory-prediction.md`

**Priority:** P1 research reference

### Hu et al. (2026)
**Estimating Maximum Usable Frequency of HF Communication Links Using the Low-Latitude Long-Range Ionospheric Radar**

DOI: https://doi.org/10.1109/TGRS.2026.3682585

**Why keep it:** Provides an independent observational approach to MUF estimation and supports Story 6.25.

**Suggested note filename:**
`2026-hu-radar-derived-hf-muf-estimation.md`

**Priority:** P1 core reference

### Aricoche, Hysell, and Morton (2026)
**Probing the Main Ionospheric Trough With an Alaskan HF Beacon Network**

DOI: https://doi.org/10.3389/fspas.2026.1848834

**Why keep it:** Demonstrates direct HF measurements of group delay, amplitude, Doppler, and spreading, and is highly relevant to richer channel validation.

**Suggested note filename:**
`2026-aricoche-alaskan-hf-beacon-network.md`

**Priority:** P1 core reference

---

## Add to `research/ionosphere-modeling/`

### Sherstyukov et al. (2026)
**Synthetic-Data-Driven Supervised Learning for Pixel-Wise Recognition of Ionogram Layer Traces**

DOI: https://doi.org/10.1029/2025JH001021

**Why keep it:** Useful reference for extracting structured ionospheric layer information from raw ionograms when pre-scaled data are insufficient.

**Suggested note filename:**
`2026-sherstyukov-ionogram-layer-segmentation.md`

**Priority:** P2

---

## Add to `research/model-evaluation/`

### Alford-Lago et al. (2026)
**Forecasting Local Ionospheric Parameters Using Transformers**

DOI: https://doi.org/10.1029/2025JH000716

**Why keep it:** Strong methodological reference for uncertainty-aware forecasting, geographic generalization, and comparison against climatological baselines.

**Suggested note filename:**
`2026-alford-lago-transformer-ionosphere-forecasting.md`

**Priority:** P2

---

# Immediate research-folder priority

If only three papers are added now, use:

1. **Hu et al. - radar-derived MUF estimation**
2. **Aricoche et al. - Alaskan HF beacon network**
3. **Li et al. - physics-informed HF ray-trajectory prediction**

These map most directly to the current Radio Atlas experiment architecture:

```text
independent physical validation
        +
richer HF channel observations
        +
future propagation acceleration
```

Sherstyukov et al. should follow when ionosonde ingestion becomes a priority.

Alford-Lago et al. should remain a core methodological reference for SolaraSphere forecasting and uncertainty calibration.

---

# November 6 research decision

The next major improvement to Radio Atlas should be **more independent observation layers, not another production prediction model**.

Prioritize:

- measured MUF where available,
- direct channel observables,
- source-aware physical validation,
- uncertainty calibration.

Then use PSK Reporter as a receiver-outcome layer on top of that physical evidence.

This gives future SolaraSphere models a much tougher and much more informative benchmark to beat.
