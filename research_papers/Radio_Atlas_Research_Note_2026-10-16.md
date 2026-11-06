# Radio Atlas research note

**Source brief:** October 16, 2026  
**Status:** Proposed roadmap additions for Radio Atlas, SolaraSphere, and SolaraSignal

The next experiment should measure whether a learned correction improves reception-probability estimates on the same paths and opportunities used by the baseline. Keep the PyRayHF/IRI geometric prediction, Story 6.17 detectability estimate, and reception evidence as separate records. An observed decode is positive evidence. A missing PSK Reporter spot stays unknown unless the trial has documented transmission and compatible receiver monitoring. Record how each negative was established, and report controlled misses separately from proxy negatives inferred from reporting activity.

## Proposed roadmap items

These are working labels for backlog triage. The evidence and replay work can begin during the single-path pilot. The learning experiment depends on an evaluated detectability baseline and a corpus with enough eligible outcomes across paths and days.

| Order | Work item | Acceptance criteria |
| --- | --- | --- |
| 1 | **Preserve source timing and replay provenance.** Retain event time and ingestion time in UTC, source identifiers, data-quality flags, and the aggregation rule. Link each evaluation to the baseline configuration, model versions, ionosphere snapshot, and observation evidence. | Replay a fixed cohort and reproduce its joins and labels, including an event on a bin boundary, a late report, and an unknown window. Retain source precision when building 15-minute evaluation bins. Track when predictor inputs became available so replay can enforce the forecast cutoff. |
| 2 | **Stratify errors by path and environment.** Derive bearing, geomagnetic latitude, local solar time, season, and geomagnetic activity for each evaluation. Start with quiet versus disturbed periods and a small number of predefined path cohorts. | Produce a cohort report with eligible and unknown counts, performance by cohort, and sparse-cell flags. Document how geographic features are calculated, including which endpoint or midpoint they represent. |
| 3 | **Pilot ionogram temporal context.** Use one station with consecutive, quality-flagged ionograms. Compare a current-sample baseline with features such as lagged foF2 and hmF2, recent trend, and time since the last usable observation. | Compare both methods on the same held-out dates against reviewed ionogram values where available. Record coverage, error, and behavior across missing intervals. In forecast evaluation, construct features from measurements available by prediction time. |
| 4 | **Associate documented disturbance events.** Add optional links between residuals and cataloged events using event time, spatial coverage, source, and a versioned matching rule. | Demonstrate matched, unmatched, and ambiguous cases. Report overlap as an association. In forecast evaluation, use only event information available at prediction time. |
| 5 | **Test a learned correction to the detectability baseline.** Freeze the baseline, then fit a simple correction using its reception probability and available path and environmental features. Preserve the original and corrected estimates side by side. | Compare Brier score and calibration on a chronological holdout and a separate evaluation of unseen TX–RX pairs. Report counts, uncertainty by path/day blocks where sample size allows, and quiet versus disturbed results. Declare the promotion criteria before scoring the holdout. Keep the experiment in research if the corpus cannot support those comparisons. |
| Parallel | **Build a small SolaraSignal HF IQ corpus.** Record labeled over-the-air 2-FSK RTTY sessions across known software implementations, with receiver settings, SNR estimate, bandwidth, and session identifiers. | Compare IQ-only, spectrum-only, and combined inputs using session-level holdouts. Report performance by SNR and bandwidth. Keep recordings from the same transmission together across splits. Treat FT8 as a separate validation task. |

### First experiment boundary

Start with the planned FT8 single-path pilot to validate the evidence and replay workflow. Expand to multiple pairs and days before fitting a correction. Use the Story 6.17 detectability baseline to score the probability of a decode for a documented transmit-and-monitor opportunity. Preserve geometric reachability as a separate output. If a future experiment corrects ionospheric state, validate it first against ionospheric measurements and then test its effect on HF path predictions. HARP-FiLM forecasts vertical total electron content (VTEC). An improvement on that target leaves the HF reception question open.

## Research folder additions

Add annotated DOI or arXiv entries to the repo’s research index, grouped by the work they inform. Use publisher titles and include a sentence on applicability.

| Priority | Article | Roadmap use |
| --- | --- | --- |
| Core · SolaraSphere | [HARP-FiLM: Global Ionospheric VTEC Forecasting With Solar–Geomagnetic Driver Conditioning and Dual-Baseline Residuals](https://doi.org/10.1029/2026JA035091) | Baseline correction and environmental conditioning. Use the study as a design reference for the experiment. |
| Core · Ionosphere inputs | [An Automatic Ionogram Scaling Method Based on Temporal Continuity Modeling](https://doi.org/10.1029/2026RS008753) | Temporal context and quality evaluation for consecutive ionograms. |
| Core · SolaraSignal | [RF Fingerprinting of DSP Implementations using Machine Learning: An Over-the-Air Case Study](https://arxiv.org/abs/2610.15494) | HF IQ corpus and evaluation by SNR and bandwidth. Index as an arXiv preprint. |
| Supporting · Regional variability | [Impact of the SW2 Tide on the Interhemispheric Asymmetry of the EIA in the American Sector: A Case Study of the September 2020 Equinox](https://doi.org/10.1029/2026JA035511) | Motivation for regional, seasonal, and local-time analysis during quiet conditions. |
| Supporting · Disturbance context | [Ionospheric Scintillation Induced by Hot Flow Anomalies via Particle Precipitation](https://doi.org/10.1029/2026AV002548) | Motivation for event associations. The measurements concern trans-ionospheric scintillation. |
| Supporting · Timing | [Characterization of High-Frequency GNSS Total Electron Content Variations](https://doi.org/10.1029/2026JA035461) | Motivation for retaining native measurement timing. “High-frequency” here refers to temporal TEC variation. |
