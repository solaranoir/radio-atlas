# Statistics Metrics

## Purpose

The Phase 3 statistics engine derives propagation and activity metrics from the
analytics rollups created by the aggregation pipeline.

These metrics provide consistent definitions for the statistics API,
historical analysis, anomaly detection, and the statistics dashboard.

Raw `spots` remain the source of truth. Statistics should use hourly or daily
rollups when those aggregates contain sufficient information for the requested
metric.

## General Semantics

- All statistical time ranges use UTC.
- Hourly rollups are the primary source for short-range and time-sensitive
  statistics.
- Daily rollups may be used for longer-range statistics.
- Band statistics may be filtered by operating mode.
- Missing SNR values contribute to activity metrics but not signal-quality
  calculations.
- Metrics describe observed activity in the Radio Atlas dataset. They do not
  imply that all amateur-radio activity on a band has been observed.
- Comparisons should use equivalent bucket resolutions and filtering criteria.

## Band-Opening Metrics

A band opening represents a period in which observed activity on a band rises
meaningfully relative to a comparison baseline.

The statistics engine does not initially attempt to classify the physical
propagation mechanism responsible for an opening.

### Observation Activity

For each band and time bucket:

`observation_activity = observation_count`

This is the fundamental measure of observed activity on a band.

### Active Station Count

For each band and time bucket:

`active_station_count = unique_sender_count + unique_receiver_count`

This metric represents observed sending and receiving participation. It is an
activity measure rather than a count of globally unique stations because the
same callsign may appear as both a sender and receiver.

### Activity Change

For consecutive equivalent buckets:

`activity_change = current_observation_count - previous_observation_count`

When the previous bucket contains observations, percentage change may also be
reported:

`activity_change_percent = ((current - previous) / previous) * 100`

Percentage change is undefined when the previous observation count is zero.

### Band-Opening Baseline

A band's opening baseline is the mean observation activity across preceding
historical buckets with the same band, mode, and bucket resolution.

For a requested baseline window containing `n` historical buckets:

`baseline_observation_count = sum(historical_observation_count) / n`

The current bucket is not included in its own baseline.

Buckets with no stored rollup row are treated as zero observed activity when
they fall within the requested baseline window. This distinguishes a period
with no observed activity from a period outside the requested historical
window.

The initial Phase 3 statistics implementation uses a configurable lookback
window. Unless a caller specifies otherwise, the default baseline window is
the preceding 24 hourly buckets for hourly statistics or the preceding 7 daily
buckets for daily statistics.

The baseline uses the same band, mode, and bucket resolution as the current
activity being evaluated.

More sophisticated time-of-day, seasonal, and rolling baselines may be
introduced by the anomaly-detection subsystem.

### Band-Opening Strength

Band-opening strength expresses current activity relative to its baseline:

`opening_strength = current_observation_count / baseline_observation_count`

Interpretation:

- values below `1.0` indicate activity below the baseline
- `1.0` indicates activity equal to the baseline
- values above `1.0` indicate activity above the baseline

Opening strength is undefined when the baseline observation count is zero.

The statistics service should expose the underlying activity and baseline
values alongside the ratio so consumers do not need to interpret the ratio in
isolation.

## Signal-Quality Metrics

Signal-quality metrics describe the observed signal-to-noise ratio (SNR) for
radio observations containing an SNR measurement.

Observations without SNR remain part of activity statistics but do not
contribute to signal-quality calculations.

### SNR Sample Count

For each bucket:

`snr_sample_count = count of observations with non-null SNR`

This value indicates how much measured signal-quality data supports the
reported SNR statistics.

### SNR Coverage

SNR coverage describes the proportion of observations containing an SNR
measurement:

`snr_coverage = snr_sample_count / observation_count`

The value ranges from `0.0` to `1.0`.

SNR coverage is undefined when `observation_count` is zero.

Consumers should consider SNR coverage when interpreting signal-quality
statistics because a small number of SNR samples may not represent the full
set of observations in the bucket.

### Average SNR

For observations containing SNR:

`average_snr_db = snr_avg_db`

Average SNR may be reported for band or station aggregates.

When combining multiple rollup buckets, averages must be weighted by each
bucket's `snr_sample_count`:

`combined_average_snr_db = sum(snr_avg_db * snr_sample_count) / sum(snr_sample_count)`

Buckets with no SNR samples do not contribute to the combined average.

### Minimum and Maximum SNR

For a requested time range:

`minimum_snr_db = minimum(snr_min_db)`

`maximum_snr_db = maximum(snr_max_db)`

Buckets without SNR samples are excluded.

These values describe the observed range and should not be interpreted as
typical signal quality.

### SNR Change

For consecutive equivalent buckets:

`snr_change_db = current_average_snr_db - previous_average_snr_db`

A positive value indicates an increase in average observed SNR, while a
negative value indicates a decrease.

SNR change is undefined if either bucket contains no SNR samples.

## Station-Activity Metrics

Station-activity metrics describe how frequently an individual callsign appears
in observations and how broadly it interacts with other observed stations.

Sender and receiver activity are measured independently because the aggregation
schema preserves those directions separately.

### Observation Activity

For a station, direction, and time range:

`station_observation_count = sum(observation_count)`

For `sender` aggregates, this represents observations in which the station was
the transmitting station.

For `receiver` aggregates, this represents observations in which the station
was the receiving station.

### Sender and Receiver Activity

Directional activity should be reported independently:

`sender_activity = sum(sender observation_count)`

`receiver_activity = sum(receiver observation_count)`

A combined activity value may also be reported:

`total_station_activity = sender_activity + receiver_activity`

The combined value represents observed participation, not a count of unique
radio contacts.

### Unique Counterparties

Within a single rollup bucket:

`unique_counterparty_count`

represents the number of distinct callsigns observed on the opposite side of
the station's activity.

For sender activity, counterparties are receiving stations.

For receiver activity, counterparties are sending stations.

Unique counterparty counts are not additive across multiple buckets. Summing
hourly `unique_counterparty_count` values may count the same callsign more than
once.

When an exact distinct-counterparty count is required across a longer time
range, the statistics engine must use a rollup whose bucket covers the complete
requested range when available, or derive the value from raw observations.

### Activity Change

For consecutive equivalent buckets:

`station_activity_change = current_observation_count - previous_observation_count`

When the previous bucket contains observations:

`station_activity_change_percent = ((current - previous) / previous) * 100`

Percentage change is undefined when the previous observation count is zero.

### Station Activity Share

A station's directional share of observed activity may be calculated against
the corresponding total activity for the same time range:

`station_activity_share = station_observation_count / total_observation_count`

The numerator and denominator must use compatible direction, time, and filter
semantics.

This metric describes the station's share of the observations represented in
Radio Atlas. It does not represent the station's share of all amateur-radio
activity.

## Solar-Condition Correlation Metrics

Solar-condition correlation metrics describe statistical relationships between
timestamped solar measurements and observed radio activity or signal quality.

These metrics identify association, not causation. A correlation between a
solar measurement and radio activity does not by itself establish that the
solar condition caused the observed propagation behavior.

### Time Alignment

Solar observations are aligned with radio-activity buckets by UTC timestamp.

For each radio bucket, the statistics engine should associate the solar
measurement appropriate to that bucket and observation type.

When multiple solar observations exist within a radio bucket, the initial
statistics implementation uses the arithmetic mean of all non-null normalized
`SolarCondition.value` measurements for the requested observation type within
that UTC bucket. Null values do not participate in the average.

This produces one solar value per UTC bucket before correlation is calculated.

Buckets without a usable solar measurement for the requested observation type
are excluded from the correlation calculation.

### Activity Correlation

For a selected solar observation type and a series of equivalent radio
buckets, activity correlation measures the relationship between the solar
measurement and:

`observation_count`

The initial correlation statistic is the Pearson correlation coefficient:

`activity_correlation = pearson(solar_value, observation_count)`

The result ranges from `-1.0` to `1.0`.

A positive value indicates that larger solar measurements tend to occur with
higher observed activity in the selected dataset. A negative value indicates
that larger measurements tend to occur with lower observed activity.

### Signal-Quality Correlation

When SNR measurements are available:

`signal_quality_correlation = pearson(solar_value, snr_avg_db)`

Only buckets containing both a usable solar measurement and at least one SNR
sample participate in the calculation.

### Correlation Sample Count

Every correlation result must include:

`sample_count = number of paired buckets used in the calculation`

The sample count makes the amount of supporting data explicit and allows API
and UI consumers to distinguish correlations based on sparse data from those
based on larger datasets.

### Insufficient Data

A correlation result is undefined when fewer than two valid paired buckets are
available or when either input series has zero variance.

Undefined correlations should be represented explicitly rather than coerced to
zero.

### Filtering

Solar correlations may be computed for:

- a specific band
- a specific operating mode
- a band and mode combination
- a requested UTC date range

All buckets participating in a single correlation calculation must use the
same temporal resolution and filtering criteria.

### Interpretation

Correlation values should be presented with the solar observation type,
radio metric, time range, bucket resolution, and sample count used in the
calculation.

The statistics engine should not assign causal labels such as "solar-caused
opening" based solely on correlation.
