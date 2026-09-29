# Anomaly Detection 

**Architecture Decision & Research Report  

| **Decision in one sentence:** Adopt an explainable hybrid detector: robust seasonal baselines for radio metrics + explicit solar-domain thresholds + deterministic scoring/classification; retain Isolation Forest as a later challenger, not the Phase 3 primary detector. |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|


# 1. Executive Decision

Story 5.1 asks the project to research threshold-based detection,
research statistical baseline methods, evaluate approaches against
historical data, and document a selected approach and rationale. This
report closes the architecture portion of that story and defines the
handoff into Stories 5.2 and 5.3. The supplied repository does not
contain a labeled anomaly corpus or a production-sized historical
database snapshot, so empirical precision/recall claims cannot
responsibly be made here. Instead, the evaluation is grounded in the
repository’s implemented data model, rollups, statistics behavior,
replay semantics, and test architecture, with an explicit validation
experiment for historical data.

| **Selected architecture:** Two-stage detection. Stage A computes expected behavior and robust deviation per metric/dimension. Stage B combines evidence into an explainable anomaly score, classification, severity, and persisted evidence record. |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 1.1 Why this fits Radio Atlas

- Radio activity is strongly seasonal in time: hour of day, day of week,
  band, mode, and station all change what “normal” means. A single
  global threshold will confuse normal propagation cycles with
  anomalies.

- The existing analytics layer already provides hourly/daily per-band
  and per-station rollups, observation counts, distinct activity counts,
  and SNR summaries. The anomaly subsystem should consume those
  artifacts instead of re-aggregating raw spots.

- The existing statistics service already computes a simple prior-window
  activity baseline. Story 5.2 can evolve this concept into robust
  seasonal baselines without breaking the statistics API.

- Solar measurements have meaningful physical scales and categories,
  making explicit threshold evidence valuable alongside learned
  historical behavior.

- Replay and timeline features benefit from deterministic, persisted
  anomalies whose “why” can be rendered in a popover. Explainability is
  therefore a product requirement, not merely a modeling preference.

## 1.2 Architecture outcome

| **Concern**    | **Decision**                                                                                           |
|----------------|--------------------------------------------------------------------------------------------------------|
| Primary method | Robust seasonal statistical baseline using median + MAD (with sparse-data fallbacks).                  |
| Solar evidence | Explicit domain thresholds/categories plus robust deviation from recent solar baseline where useful.   |
| Scoring        | Normalized per-signal deviation → weighted composite score; preserve component evidence.               |
| Classification | Rule-based evidence mapping to solar / propagation / station, with unknown/mixed available internally. |
| Severity       | Deterministic score bands, gated by sample sufficiency and persistence.                                |
| ML detector    | Isolation Forest as a later offline challenger/secondary signal after Phase 3 validation data exists.  |
| Persistence    | Persist anomaly event + evidence snapshot; do not persist every intermediate score indefinitely.       |

# 2. Repository Findings That Constrain the Design

The anomaly design is deliberately shaped around code that already
exists in the supplied backend rather than around an abstract greenfield
detector.

| **Existing artifact**            | **Observed behavior**                                                                                                                | **Architectural implication**                                                                                    |
|----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| analytics_band_hourly / daily    | Band + mode buckets include observation_count, unique senders/receivers, SNR count/min/max/avg. Null band observations are excluded. | Primary propagation feature source. Detector must acknowledge band-resolved coverage.                            |
| analytics_station_hourly / daily | Callsign + direction buckets include activity, unique counterparties, and SNR summaries.                                             | Primary station feature source; sender and receiver directions should remain distinct evidence.                  |
| StatisticsService baseline       | Hourly baseline = prior 24 buckets; daily = prior 7; calculate_activity_baseline divides total counts by expected bucket count.      | Useful seed, but not seasonal or robust. Replace/extend for anomaly baselines rather than duplicating it.        |
| Band opening strength            | observation_count / baseline_observation_count.                                                                                      | Can become an interpretable supporting feature, but ratio alone is unstable when expected activity is near zero. |
| Solar conditions                 | Timestamped NOAA observations remain in solar_conditions rather than analytics rollups.                                              | Align solar evidence by UTC windows; add a solar rollup only if profiling justifies it.                          |
| UTC aggregation semantics        | Hourly and daily buckets align to UTC; range queries are half-open.                                                                  | Anomaly windows and persistence timestamps must use the same UTC \[start, end) convention.                       |
| Replay/timeline architecture     | Historical state is driven by time windows and persisted analytical artifacts.                                                       | Anomalies should be addressable by bucket/window and reusable as timeline markers.                               |

# 3. Detection Requirements

## 3.1 What counts as an anomaly?

For Radio Atlas, an anomaly is not merely an extreme measurement. It is
a time-bounded departure from an expected state that is large enough,
sufficiently supported by data, and useful enough to surface during
analytics or replay. The detector must separate “rare” from
“interesting” as much as the available evidence permits.

| **Class**          | **Examples of evidence**                                                                                                           | **Primary dimensions**         |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| Propagation        | Unexpected activity surge/drop; unusual SNR shift; unusually broad station participation; band opening inconsistent with baseline. | bucket × band × mode           |
| Station            | Callsign activity surge/drop; counterparty diversity jump; sender/receiver asymmetry; station SNR departure.                       | bucket × callsign × direction  |
| Solar              | Kp excursion/category; Bz or solar-wind departure; F10.7/sunspot departure; solar event temporally aligned with radio change.      | bucket × observation_type      |
| Mixed / correlated | Strong radio departure plus temporally aligned solar evidence.                                                                     | radio dimension + solar window |

## 3.2 Non-functional requirements

- Explainable: every persisted event must retain enough evidence to
  answer “why was this flagged?”

- Deterministic and reproducible for a given baseline version and source
  window.

- Sparse-data aware: absence of samples must not silently become
  evidence of a radio blackout.

- Idempotent for backfills/reruns, matching the aggregation pipeline’s
  rebuild model.

- Efficient over rollups; raw spots should be used for
  drill-down/verification, not the normal scoring loop.

- Versioned: baseline/scoring configuration must be identifiable so
  historical events remain interpretable after tuning.

# 4. Candidate Approaches

## 4.1 Static / domain thresholds

A threshold detector flags a value or derived metric when it crosses a
configured bound. It is excellent when a domain already supplies
meaningful levels, and weak when normal behavior varies strongly by
context.

| **Strengths**                                                                                                              | **Weaknesses**                                                                                                                                    |
|----------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| Fast, deterministic, trivial to test; excellent explainability; useful for known solar categories and data-quality guards. | Poor fit for station/band activity because “normal” varies by time and dimension; configuration grows combinatorially; abrupt cliff at threshold. |

## 4.2 Mean / standard-deviation Z-score

Classic Z-scores normalize deviation from a mean by standard deviation.
They are familiar and cheap, but the same extreme points being detected
can distort the mean and standard deviation. NIST also cautions that
ordinary Z-score outlier identification can be misleading, particularly
with small samples. For Radio Atlas this is especially awkward for
bursty, skewed count data.

## 4.3 Robust modified Z-score using median + MAD

Median Absolute Deviation (MAD) measures typical distance from the
median and is a robust alternative to standard deviation. A modified
Z-score based on median and MAD is substantially less sensitive to a few
extreme historical buckets. This is a strong match for radio activity,
where genuine openings can otherwise contaminate the baseline used to
find future openings.

> median = median(history)  
> MAD = median(abs(x - median) for x in history)  
> robust_z = 0.6745 \* (current - median) / MAD

When MAD is zero, the detector must not divide by zero or manufacture
infinite certainty. The proposed fallback is: use an
absolute/minimum-scale guard, then IQR or a configured floor if
sufficient history exists; otherwise report insufficient baseline.

## 4.4 Seasonal robust baseline

The robust statistic becomes much more useful when history is selected
from comparable seasonal slots. For an hourly bucket, compare with the
same hour-of-day across prior days/weeks, preferably with
weekday/weekend or day-of-week context once enough history exists. For
daily buckets, compare comparable days across prior weeks. This directly
implements Story 5.2’s seasonal and diurnal adjustment requirement.

## 4.5 EWMA / control-chart family

Exponentially weighted moving averages and statistical process-control
limits are good at detecting sustained shifts and can adapt to gradual
drift. They are valuable as a persistence/trend signal, but less
intuitive as the only baseline for a system whose expected level changes
cyclically. A future detector can use EWMA on residuals after seasonal
normalization.

## 4.6 Isolation Forest

Isolation Forest is an unsupervised multivariate detector that
recursively partitions feature space; points isolated with shorter paths
are treated as more anomalous. It is attractive when anomalies arise
from combinations of individually ordinary features. However, its scores
are less directly interpretable, it introduces training/configuration
lifecycle concerns, and the repository currently has no labeled anomaly
set with which to calibrate contamination or severity. It is therefore a
useful challenger model, not the Phase 3 source of truth.

## 4.7 LOF / One-Class SVM and heavier forecasting models

Local Outlier Factor can detect local-density deviations, while
One-Class SVM learns a boundary around normal observations.
Forecasting/decomposition methods can explicitly model seasonality.
These approaches add preprocessing, parameter sensitivity, retraining,
and operational complexity. They should be reconsidered only after the
baseline detector produces a labeled review corpus and failure modes
that justify the complexity.

# 5. Comparative Evaluation

| **Approach**           | **Seasonality** | **Sparse data** | **Explainability** | **Ops cost** | **Multivariate** | **Phase 3 fit** |
|------------------------|-----------------|-----------------|--------------------|--------------|------------------|-----------------|
| Static thresholds      | Low             | High            | Excellent          | Very low     | Low              | Supporting      |
| Mean + std Z-score     | Medium\*        | Medium          | High               | Low          | Low              | Weak            |
| Median + MAD           | Medium\*        | Medium          | High               | Low          | Low              | Strong          |
| Seasonal median + MAD  | High            | Medium          | High               | Low–medium   | Low              | PRIMARY         |
| EWMA/control chart     | Medium          | Medium          | High               | Low–medium   | Low              | Secondary       |
| Isolation Forest       | Implicit        | Medium          | Medium–low         | Medium       | High             | Challenger      |
| LOF / One-Class SVM    | Implicit        | Low–medium      | Low                | Medium–high  | High             | Defer           |
| Forecast/decomposition | High            | Medium          | Medium             | High         | Medium           | Defer           |

\* Seasonality is only present if the baseline cohort is explicitly
segmented by time context; the statistic alone does not create it.

| **Decision rationale:** Seasonal median + MAD wins the architecture trade-off because it is robust, cheap, explainable, deterministic, and naturally maps onto the existing hourly/daily rollups. Threshold rules complement it where physical/domain semantics are stronger than learned history. |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 6. Proposed Detection Architecture

## 6.1 Pipeline

> rollups / solar_conditions  
> │  
> ▼  
> BaselineService ──► BaselineSnapshot (expected, scale, sample_count,
> quality)  
> │  
> ▼  
> DeviationScorer ──► SignalEvidence\[\] (metric, actual, expected,
> deviation)  
> │  
> ▼  
> AnomalyClassifier ──► type + composite score + severity +
> explanation  
> │  
> ▼  
> AnomalyRepository ──► persisted event ──► API / timeline / replay

## 6.2 Baseline cohorts

| **Target**     | **Preferred cohort**                                                     | **Fallback**                                                                |
|----------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Band hourly    | same band + mode + UTC hour; prior 28 comparable days                    | same band + mode, recent 7–28 days; then insufficient                       |
| Band daily     | same band + mode + weekday; prior 8–12 weeks                             | same band + mode, recent 28–84 days                                         |
| Station hourly | same callsign + direction + UTC hour; prior 28 days                      | recent station buckets; global station baseline only as last-resort context |
| Station daily  | same callsign + direction + weekday; prior 8–12 weeks                    | recent station daily buckets                                                |
| Solar          | observation-type-specific recent/seasonal history plus domain thresholds | domain threshold evidence where available                                   |

The exact windows are tuning defaults, not hard-coded truths. Story 5.2
should place them in versioned configuration and measure baseline
coverage before locking them.

## 6.3 Baseline snapshot contract

> BaselineSnapshot  
> dimension_type: band \| station \| solar  
> dimension_key: stable serialized key  
> metric: observation_count \| avg_snr_db \| ...  
> resolution: hour \| day  
> expected_value: float  
> scale: float \| null  
> sample_count: int  
> method: seasonal_median_mad \| fallback\_\*  
> cohort_start / cohort_end: datetime  
> baseline_version: str  
> quality: sufficient \| sparse \| degenerate

## 6.4 Evidence contract

> SignalEvidence  
> metric  
> actual_value  
> expected_value  
> signed_deviation  
> anomaly_magnitude \# non-negative normalized magnitude  
> direction: high \| low  
> weight  
> baseline_quality  
> threshold_name: str \| null

## 6.5 Composite score

Each usable signal is converted to a bounded magnitude before
combination so one pathological metric cannot dominate forever. A simple
initial function is min(abs(robust_z), cap) / cap. The event score is
the weighted mean of available evidence, optionally boosted when
multiple independent signals agree. Missing evidence is excluded from
the denominator rather than treated as normal.

> component = min(abs(robust_z), Z_CAP) / Z_CAP  
> score = sum(weight_i \* component_i) / sum(weight_i for available
> signals)

The persisted event should retain the raw robust Z-score and evidence
even if the public score is normalized to 0..1. This prevents the
UI-friendly score from becoming the only forensic record.

# 7. Classification and Severity

## 7.1 Classification rules

| **Evidence pattern**                                                                       | **Classification**                                                   |
|--------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| Solar threshold/deviation dominates without meaningful radio departure                     | solar                                                                |
| Band/mode activity or SNR departure dominates                                              | propagation                                                          |
| One station’s activity/counterparty/SNR departure dominates while broader band is ordinary | station                                                              |
| Radio departure and solar evidence coincide                                                | propagation with solar evidence; optionally internal mixed subtype   |
| No evidence family clearly dominates                                                       | unknown internally; do not surface until confidence threshold is met |

Classification should describe the evidence, not claim physical
causation. A geomagnetic event occurring near a propagation change is
correlation evidence; Radio Atlas should not state that the solar event
caused the radio behavior unless a future causal model supports that
claim.

## 7.2 Initial severity model

| **Severity** | **Proposed meaning**                                                                                            |
|--------------|-----------------------------------------------------------------------------------------------------------------|
| info         | Interesting deviation, useful in analytics but below default alert/marker prominence.                           |
| minor        | Clear anomaly with sufficient baseline and at least one strong signal.                                          |
| major        | Large departure, or multiple agreeing evidence signals, sustained/persistent enough to reduce one-bucket noise. |
| critical     | Reserved for exceptional multi-signal events or explicit severe solar-domain conditions; intentionally rare.    |

Story 5.3 should calibrate numeric cutoffs from historical score
distributions rather than declaring arbitrary final values in Story 5.1.
Until calibration, thresholds belong in configuration and tests should
assert monotonic behavior rather than pretend the cutoffs are
scientifically validated.

# 8. Historical Evaluation Plan

The roadmap asks for evaluation against historical data. The repository
supplied for this design contains code and tests, not a labeled
production history, so this report specifies the experiment rather than
fabricating results.

1.  Backfill hourly/daily rollups across the available PSK history and
    materialize candidate baselines without looking forward in time.

2.  Generate candidate scores for seasonal MAD, simple rolling mean,
    mean/std Z-score, and the threshold-only baseline. Run Isolation
    Forest offline on the same feature windows as a challenger.

3.  Build a small “known events” set from independently timestamped
    solar/space-weather events plus manually reviewed radio windows.
    Keep the source and review label separate from detector output.

4.  Measure event yield per day/band/station, score distribution,
    baseline coverage, duplicate-event rate, persistence, and reviewer
    usefulness. Where ground-truth labels are defensible, measure
    precision/recall; otherwise report reviewed hit rate and
    false-positive categories.

5.  Stress sparse stations, quiet bands, missing SNR, null bands,
    ingestion gaps, daylight/diurnal transitions, and major activity
    bursts.

6.  Tune configuration on one historical period and evaluate on a later
    holdout period to avoid “tuning the telescope to the comet already
    seen.”

## 8.1 Acceptance evidence for selecting the detector

- Robust seasonal baseline produces fewer obvious diurnal false
  positives than a simple prior-window mean.

- Known strong events receive higher scores than ordinary comparable
  buckets without requiring per-band hand tuning.

- Sparse dimensions become “insufficient baseline” rather than extreme
  anomalies.

- Backfill reruns reproduce identical anomaly IDs/evidence under the
  same detector version.

- A reviewer can explain every surfaced event from persisted evidence
  without rerunning an opaque model.

# 9. Persistence Model Recommendation

Story 5.3 requires anomaly persistence and Story 5.4 must link anomalies
to source observations. Persist the event and its evidence snapshot.
Baseline tables belong to Story 5.2 and should be independently
refreshable.

> anomalies  
> id UUID / stable deterministic key  
> bucket_start, bucket_end, resolution  
> anomaly_type, severity, score  
> dimension_type, dimension_key  
> primary_metric, direction  
> detector_version, baseline_version  
> evidence JSONB  
> source_observation_start/end  
> created_at, updated_at  
> UNIQUE(detector_version, dimension_key, bucket_start, primary_metric)

JSONB is appropriate for the evidence envelope because signal sets will
evolve, while the columns required for filtering, ordering, and joining
remain relational. Story 5.3 should validate this choice against the
project’s migration conventions before implementation.

## 9.1 Baseline persistence

Baseline storage should support per-band and per-station expected
behavior as required by Story 5.2. Prefer storing compact baseline
parameters/snapshots (expected, scale, sample count, cohort metadata,
version) rather than duplicating all historical samples. Rebuild jobs
can derive snapshots from analytics rollups.

# 10. Repository Integration Plan

> app/analytics/anomalies/  
> \_\_init\_\_.py  
> models.py \# BaselineSnapshot, SignalEvidence, AnomalyCandidate  
> baseline.py \# robust/seasonal calculations and fallbacks  
> scoring.py \# deviation normalization + composite scoring  
> classification.py \# type/severity evidence rules  
> service.py \# orchestration  
> persistence.py \# anomaly + baseline storage  
> queries.py \# rollup/solar reads  
> runtime.py \# backfill/incremental execution  
>   
> tests/unit/analytics/anomalies/  
> tests/integration/analytics/test_anomalies.py

This mirrors the existing analytics/aggregation and analytics/statistics
organization rather than introducing a new architectural vocabulary.

## 10.1 Reuse boundaries

- Reuse existing rollup models/queries where their return shape is
  sufficient; do not make anomaly code query raw spots by default.

- Extract or generalize baseline utilities only when doing so keeps
  StatisticsService behavior stable. Avoid a large refactor merely to
  achieve theoretical reuse.

- Use the existing SQLAlchemy session/dependency patterns and Alembic
  migration style.

- Keep detector math pure and unit-testable; database/service
  orchestration should be thin.

- Version baseline/scoring configuration explicitly. Configuration
  changes must not silently reinterpret already-persisted anomalies.

# 11. Edge Cases and Failure Modes

| **Case**                 | **Required behavior**                                                                                                                           |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| No history / new station | No anomaly from baseline method; quality=insufficient. Domain threshold evidence may still apply where meaningful.                              |
| MAD = 0                  | Use configured scale floor/fallback; never divide by zero.                                                                                      |
| Expected activity ≈ 0    | Do not rely on ratio/opening_strength alone; use count-aware absolute evidence and minimum-support rules.                                       |
| Missing SNR              | Exclude SNR evidence; observation activity remains valid.                                                                                       |
| Null band                | Not represented in band rollups; never infer “quiet band” from missing null-band data.                                                          |
| Ingestion outage         | Suppress radio-drop anomalies if ingestion/provider health indicates missing data. This cross-check should be added before production alerting. |
| Single-bucket spike      | May be info/minor; persistence or multi-signal agreement can raise severity.                                                                    |
| Solar/radio coincidence  | Label as correlated evidence, not proven cause.                                                                                                 |
| Baseline drift           | Refresh snapshots on schedule and preserve baseline_version used for each event.                                                                |
| Backfill                 | Score chronologically with no future leakage; reruns idempotent.                                                                                |

# 12. Story 5.2 / 5.3 Handoff

## Story 5.2: Implement baseline modeling

- Implement robust median/MAD primitives and degenerate/sparse
  fallbacks.

- Implement seasonal cohort selection for hourly/daily band and station
  dimensions.

- Implement baseline snapshot storage, versioning, refresh, and
  backfill.

- Add coverage metrics: dimensions with sufficient/sparse/degenerate
  baselines.

- Write deterministic tests around UTC bucket selection and
  no-future-data leakage.

## Story 5.3: Implement anomaly scoring

- Implement per-metric SignalEvidence and bounded composite scoring.

- Implement type classification and configurable severity thresholds.

- Implement persistence with evidence snapshots and idempotent
  uniqueness.

- Add suppression/quality gates for sparse baselines and known ingestion
  gaps.

- Calibrate thresholds using the historical evaluation plan before
  calling defaults final.

# 13. Architecture Decision Record

| **Field**             | **Decision**                                                                                                                                              |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Status                | Accepted for Phase 3 implementation; numeric calibration remains experimental.                                                                            |
| Context               | Radio Atlas needs anomaly markers over seasonal, sparse, heterogeneous radio and solar time series, with replay-friendly explanations.                    |
| Decision              | Hybrid seasonal robust statistical detector + domain thresholds + deterministic composite classification/severity.                                        |
| Positive consequences | Explainable; low operational overhead; uses current rollups; easy to backfill/test; natural timeline integration.                                         |
| Negative consequences | Univariate evidence may miss subtle multivariate anomalies; seasonal cohorts need enough history; thresholds still require calibration.                   |
| Alternatives deferred | Isolation Forest, LOF, One-Class SVM, forecasting/decomposition as primary detector.                                                                      |
| Revisit trigger       | Sufficient reviewed anomaly corpus exists and shows systematic patterns the robust detector misses, or false positives remain high after seasonal tuning. |

# 14. Research Sources and Repository Basis

Repository basis (supplied backend.zip): analytics aggregation
schema/models/jobs; statistics metrics/service/queries; replay
architecture/streaming; NOAA and PSK Reporter models; migrations and
tests. Roadmap basis: Phase 3 Story 5.1–5.5 and related timeline/replay
requirements.

External research used to evaluate statistical approaches:

- NIST/SEMATECH Engineering Statistics Handbook, “Detection of
  Outliers”: Z-scores, modified Z-scores, and masking considerations.

- NIST Dataplot reference, “Median Absolute Deviation”: MAD as a robust
  alternative to standard deviation and scaled MAD behavior.

- NIST/SEMATECH Engineering Statistics Handbook, Process Monitoring and
  Control: historical-baseline/control concepts and time-series
  monitoring.

- scikit-learn documentation, IsolationForest: isolation-path anomaly
  scoring and estimator behavior.

- scikit-learn outlier-detection benchmark: algorithm performance varies
  by dataset and hyperparameter sensitivity.

Research note: no external source was used to assert a final numeric
Radio Atlas anomaly threshold. Those values require project-specific
historical calibration.

# Appendix A. Suggested Initial Configuration Surface

> anomaly_detection:  
> detector_version: "seasonal-mad-v1"  
> baseline:  
> hourly_lookback_days: 28  
> daily_lookback_weeks: 12  
> minimum_samples: 8  
> mad_scale_floor: \<calibrate\>  
> scoring:  
> robust_z_cap: \<calibrate\>  
> weights:  
> observation_count: \<calibrate\>  
> average_snr_db: \<calibrate\>  
> active_station_count: \<calibrate\>  
> severity:  
> info: \<calibrate\>  
> minor: \<calibrate\>  
> major: \<calibrate\>  
> critical: \<calibrate\>  
> persistence:  
> require_consecutive_buckets_for_major: \<calibrate\>

The placeholders are intentional. Story 5.1 selects the method; the
historical evaluation should calibrate the constants.

# Appendix B. Definition of Done for Story 5.1

- [x] Threshold-based detection researched and scoped to its strongest
  use cases.

- [x] Statistical baseline approaches compared, including robustness and
  seasonality.

- [x] ML/unsupervised alternatives considered and deliberately deferred
  as primary architecture.

- [x] Repository constraints and reuse points documented.

- [x] Selected approach and rationale recorded.

- [x] Historical-data evaluation protocol defined without inventing
  results.

- [x] Clear implementation handoff produced for Stories 5.2 and 5.3.
