**SOLARASPHERE · RADIO ATLAS**

Story 4.1: Timeline Data Model Design

*Software Architecture Decision & Implementation Contract*

Phase 3 · Analytics and Replay  
Prepared from the supplied backend repository artifacts · 29 September
2026

**Decision in one line**

Model the timeline as a derived, zoom-aware read model over existing
analytics rollups, with an extensible marker contract and no new
timeline persistence table in Story 4.1.

# 1. Software Architect Agent Charter

Role: Radio Atlas Software Architect for Story 4.1. The agent is
responsible for producing a timeline model that fits the repository as
it exists, preserves established temporal semantics, and gives Story 4.2
a concrete API contract without prematurely implementing the endpoint.

| **Concern**           | **Architect instruction**                                                                                                                         |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| Source of truth       | Treat raw spots as immutable historical truth; derived analytics are rebuildable read models.                                                     |
| Repository fit        | Prefer existing SQLAlchemy models, analytics rollups, replay boundaries, FastAPI/Pydantic conventions, and UTC semantics over new infrastructure. |
| Time semantics        | Use observed_at for historical ordering. Use inclusive start and exclusive end everywhere: \[start_time, end_time).                               |
| Scope discipline      | Story 4.1 designs density buckets, notable-activity markers, and the timeline contract. It does not implement GET /api/v1/timeline.               |
| Forward compatibility | Leave clean extension points for anomaly markers and additional resolutions without changing the client-facing shape.                             |
| Verification          | Every decision must map to an existing artifact, an explicit Story 4.1 requirement, or a clearly labeled architectural recommendation.            |

# 2. Story 4.1 Objective and Acceptance Test

Phase 3 turns accumulated observation history into an analytical and
replay platform. Epic 4 requires a timeline that can summarize
historical activity, expose notable events, and act as the scrub surface
that later drives ReplaySession seek. Story 4.1 specifically requires
density buckets, event markers, and a documented data contract. The
acceptance criterion is that timeline data supports scrubbing across the
full history.

- Design timeline density buckets.

- Design event markers for notable activity.

- Document the timeline data contract.

Interpretation of “full history”: the contract must remain bounded in
response size as the stored history grows. It does not require
raw-observation precision at every zoom level. Replay remains
responsible for precise historical observation retrieval after the user
seeks.

# 3. Existing Repository Constraints

| **Artifact**                | **Observed contract**                                                              | **Timeline consequence**                                                                    |
|-----------------------------|------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| spots                       | Raw observations include observed_at, band, mode, callsigns, SNR, and station IDs. | Raw observations remain authoritative; timeline should not duplicate them.                  |
| analytics_band_hourly       | UTC hour + band + mode, with observation and station/SNR measures.                 | Primary source for normal timeline density.                                                 |
| analytics_band_daily        | UTC day + band + mode with equivalent measures.                                    | Primary source for long-range/full-history density.                                         |
| ReplayActivityBucket        | bucket_start + observation_count.                                                  | Existing replay code already expresses activity density as a simple time bucket.            |
| build_replay_activity_query | Sums analytics_band_hourly observation_count grouped by bucket_start.              | Timeline density should reuse this aggregation idea rather than create competing semantics. |
| Replay architecture         | Historical range and playback windows are \[start, end); observed_at is canonical. | Timeline range and bucket boundaries must be identical.                                     |
| Statistics API              | Pydantic response models expose explicit resolution and UTC bucket timestamps.     | Timeline API should follow the same transport conventions.                                  |

# 4. Architectural Decision

Use a derived timeline read model. Story 4.1 should not introduce a
timeline database table. Density is calculated from the existing band
rollups, collapsed across band and mode unless filters are later added.
Event markers are returned through a stable marker contract whose
providers may initially derive markers from activity data and later
include persisted anomaly records.

Why this is the best fit: the analytics schema explicitly names timeline
density generation as a consumer of band rollups; raw spots remain the
source of truth; rollups are designed for rebuild/backfill; and replay
already has an hourly activity query. A separate timeline table would
duplicate derived state before profiling demonstrates a need.

# 5. Timeline Density Bucket Model

A density bucket answers one UI question: “How much radio activity
occurred in this visible slice of historical time?” It intentionally
carries fewer dimensions than a statistics response. The scrubber needs
shape and intensity first; detailed statistics can be fetched
separately.

| **Field**          | **Type**       | **Required** | **Semantics**                                                                                |
|--------------------|----------------|--------------|----------------------------------------------------------------------------------------------|
| start_time         | datetime (UTC) | yes          | Inclusive bucket start.                                                                      |
| end_time           | datetime (UTC) | yes          | Exclusive bucket end.                                                                        |
| observation_count  | integer \>= 0  | yes          | Total spots represented by the bucket after collapsing band/mode rows.                       |
| normalized_density | float 0..1     | yes          | Count normalized against the maximum bucket count in this response; 0 when all counts are 0. |
| has_activity       | boolean        | yes          | Convenience flag: observation_count \> 0.                                                    |

## 5.1 Resolution policy

Story 4.2 requires zoom-level-aware resolution. The data model therefore
names resolution explicitly while keeping the first implementation
aligned to rollups that already exist.

| **Resolution** | **Backer**            | **Recommended use**                                  | **Notes**                                                                      |
|----------------|-----------------------|------------------------------------------------------|--------------------------------------------------------------------------------|
| hour           | analytics_band_hourly | Focused ranges up to 14 days                         | Native stored resolution; sum observation_count across band and mode per hour. |
| day            | analytics_band_daily  | Ranges longer than 14 days and full-history overview | Native stored resolution; bounded response growth.                             |

The 14-day switch is a recommended API default, not a database
invariant. At 14 days, hourly density yields at most 336 buckets, which
is comfortably renderable. Story 4.2 may accept an explicit resolution
override or a client zoom hint. Future finer resolutions (for example
5-minute buckets) can be added from raw spots without changing the
bucket contract, but Story 4.1 does not require or persist them.

## 5.2 Bucket completeness

Return a contiguous bucket series for the requested range, including
zero-count buckets. Sparse database rows are useful for storage, but a
scrubber benefits from a stable temporal axis. The service layer should
fill missing aligned buckets with observation_count=0 and
normalized_density=0. This prevents visual gaps from being confused with
missing API data.

## 5.3 Alignment and clipping

- All bucket boundaries are UTC.

- Requested timeline range is \[start_time, end_time).

- Database selection uses bucket_start \>= aligned_start and
  bucket_start \< end_time.

- Response metadata preserves the exact requested range even when source
  buckets are aligned to hour/day boundaries.

- A scrub target is a UTC instant. Seeking to a bucket boundary uses
  that instant directly, preserving ReplaySession semantics.

# 6. Event Marker Model

Markers annotate the density field with moments or intervals worth
noticing. The marker model should describe an event without coupling the
timeline to a particular detector. This is important because anomaly
persistence belongs to Epic 5, after Story 4.1.

| **Field**         | **Type**                      | **Required** | **Semantics**                                                                                                          |
|-------------------|-------------------------------|--------------|------------------------------------------------------------------------------------------------------------------------|
| id                | string                        | yes          | Stable identifier within the marker source, suitable for UI keys and detail lookup.                                    |
| event_type        | string/enum                   | yes          | Machine-readable category, initially activity_peak; extensible to solar_anomaly, propagation_anomaly, station_anomaly. |
| start_time        | datetime UTC                  | yes          | Inclusive event start.                                                                                                 |
| end_time          | datetime UTC                  | no           | Exclusive event end for interval events; null for point events.                                                        |
| severity          | info \| low \| medium \| high | yes          | Presentation-neutral relative importance.                                                                              |
| label             | string                        | yes          | Short human-readable marker label.                                                                                     |
| source            | string/enum                   | yes          | Producer, initially timeline_activity; later anomaly_detection or solar_conditions.                                    |
| observation_count | integer                       | no           | Activity magnitude when meaningful.                                                                                    |
| metadata          | object                        | yes          | Small extensible object; defaults to {}. Do not embed raw observations.                                                |

## 6.1 Initial notable-activity rule

For Story 4.2, activity markers can be derived from the same density
series rather than persisted. A conservative first rule is to mark local
activity peaks only when a bucket is both a local maximum and materially
above the visible-range baseline. The exact threshold belongs in the
implementation story and tests, not in the storage schema. When Epic 5
introduces persisted anomalies, an anomaly marker provider can map those
records into the same TimelineEvent shape.

This avoids a circular dependency: Epic 4 can ship before anomaly
detection while the frontend receives a marker contract that will not
need to be redesigned later.

# 7. Timeline Data Contract

Recommended response model for the future GET /api/v1/timeline endpoint:

class TimelineBucket(BaseModel):  
start_time: datetime  
end_time: datetime  
observation_count: int  
normalized_density: float  
has_activity: bool  
  
class TimelineEvent(BaseModel):  
id: str  
event_type: str  
start_time: datetime  
end_time: datetime \| None = None  
severity: Literal\["info", "low", "medium", "high"\]  
label: str  
source: str  
observation_count: int \| None = None  
metadata: dict\[str, object\] = {}  
  
class TimelineResponse(BaseModel):  
start_time: datetime  
end_time: datetime  
resolution: Literal\["hour", "day"\]  
bucket_seconds: int  
buckets: list\[TimelineBucket\]  
events: list\[TimelineEvent\]

## 7.1 Example JSON

{  
"start_time": "2026-09-01T00:00:00Z",  
"end_time": "2026-09-03T00:00:00Z",  
"resolution": "hour",  
"bucket_seconds": 3600,  
"buckets": \[  
{  
"start_time": "2026-09-01T00:00:00Z",  
"end_time": "2026-09-01T01:00:00Z",  
"observation_count": 1842,  
"normalized_density": 0.63,  
"has_activity": true  
}  
\],  
"events": \[  
{  
"id": "activity-20260901T031500Z",  
"event_type": "activity_peak",  
"start_time": "2026-09-01T03:00:00Z",  
"end_time": "2026-09-01T04:00:00Z",  
"severity": "info",  
"label": "Elevated radio activity",  
"source": "timeline_activity",  
"observation_count": 2911,  
"metadata": {}  
}  
\]  
}

# 8. Query and Service Design for Story 4.2

Story 4.1 does not implement the endpoint, but the model should make
implementation obvious. The recommended dependency flow mirrors the
repository’s current layering:

GET /api/v1/timeline  
↓  
TimelineService  
↓  
TimelineDensitySource + TimelineEventSource(s)  
↓ ↓  
analytics_band_hourly/daily derived activity markers  
later: anomaly persistence

Density query shape: select bucket_start and SUM(observation_count),
filter by the half-open time range, group by bucket_start, and order
ascending. This is the same shape already used by
build_replay_activity_query for hourly activity. The timeline
implementation should generalize it to hourly/daily models rather than
create unrelated SQL.

SELECT bucket_start, SUM(observation_count) AS observation_count  
FROM analytics_band_hourly  
WHERE bucket_start \>= :start_time  
AND bucket_start \< :end_time  
GROUP BY bucket_start  
ORDER BY bucket_start;

## 8.1 Recommended repository artifacts

| **Artifact**                             | **Purpose**                                                                          |
|------------------------------------------|--------------------------------------------------------------------------------------|
| app/timeline/models.py                   | Frozen domain dataclasses or equivalent for TimelineDensityBucket and TimelineEvent. |
| app/timeline/queries.py                  | Hourly/daily density query builders; no FastAPI dependency.                          |
| app/timeline/service.py                  | Resolution selection, zero-fill, normalization, event-source composition.            |
| app/api/routes/timeline.py               | Story 4.2 transport layer and Pydantic response models.                              |
| tests/unit/timeline/                     | Resolution, bucket filling, normalization, marker mapping tests.                     |
| tests/integration/timeline/              | Database-backed range and aggregation correctness tests.                             |
| docs/architecture/Timeline_Data_Model.md | Repository copy of this architecture contract.                                       |

# 9. API Input Contract Recommendation

| **Parameter**  | **Type**            | **Default** | **Rule**                                                                  |
|----------------|---------------------|-------------|---------------------------------------------------------------------------|
| start_time     | datetime UTC        | required    | Inclusive. Reuse validate_time_range behavior.                            |
| end_time       | datetime UTC        | required    | Exclusive and greater than start_time.                                    |
| resolution     | auto \| hour \| day | auto        | auto chooses bounded bucket count; explicit values support frontend zoom. |
| include_events | boolean             | true        | Allows density-only requests during rapid scrubbing/zooming if needed.    |

Do not add band, mode, or station filters to Story 4.1 unless product
requirements demand them. The roadmap asks for a global timeline scrub
surface, and premature filtering expands cache/query semantics. The
response model can accept such filters later without changing bucket
identity.

# 10. Invariants and Edge Cases

| **Case**                         | **Required behavior**                                                                                                            |
|----------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Boundary observation             | An observation at end_time is excluded; one at start_time is included.                                                           |
| Empty range data                 | Return aligned zero-density buckets and no events, not an error.                                                                 |
| Partial first/last source bucket | Metadata preserves requested range; bucket timestamps remain canonical aligned UTC boundaries.                                   |
| Late-arriving spots              | Timeline changes after analytics bucket recomputation; no timeline-specific repair is needed.                                    |
| Missing band                     | Such spots are absent from band rollups by existing design, so density based on band rollups does not count them.                |
| Mode multiplicity                | Counts are safe to sum across band/mode rows because each band-eligible spot contributes to exactly one band+mode aggregate row. |
| DST/local time                   | No special behavior. Storage and contract remain UTC; localization is a frontend concern.                                        |
| Huge history                     | auto resolution selects daily buckets, preventing response size from growing hourly across the entire history.                   |

Important known limitation: because current band rollups exclude spots
whose band is null, rollup-derived timeline density is “band-resolved
radio activity,” not a mathematically exact count of every raw spot.
This is consistent with the existing analytics design. If product
semantics require every raw spot, Story 4.2 should either document the
distinction or profile a separate raw-count path before changing the
model.

# 11. Story 4.1 Acceptance Mapping and Test Plan

| **Requirement**           | **Design evidence**                                                 | **Story 4.2/4.4 test**                                                     |
|---------------------------|---------------------------------------------------------------------|----------------------------------------------------------------------------|
| Scrub across full history | Daily rollup resolution plus bounded auto-selection.                | Request earliest-to-latest seeded history; verify ordered bounded buckets. |
| Density buckets           | Explicit TimelineBucket contract with count and normalized density. | Verify sums against analytics rollups at hour/day resolution.              |
| Event markers             | Stable TimelineEvent contract independent of detector.              | Verify marker timestamps fall within range and map to correct bucket.      |
| Zoom awareness            | Resolution is explicit and auto-selectable.                         | Verify threshold selection and explicit override.                          |
| Replay synchronization    | Same UTC \[start,end) semantics and seek timestamp domain.          | Scrub to boundary; verify ReplaySession seek receives exact UTC instant.   |

- Unit: normalization with zero, one, and uneven bucket counts.

- Unit: zero-fill across missing hourly/daily database rows.

- Unit: resolution auto-selection at threshold boundaries.

- Unit: marker mapping and stable IDs.

- Integration: hourly density equals
  SUM(analytics_band_hourly.observation_count) by bucket.

- Integration: daily density equals
  SUM(analytics_band_daily.observation_count) by bucket.

- Integration: end_time exclusivity and chronological ordering.

- Contract: OpenAPI response shape and UTC-aware datetime serialization.

# 12. Decisions, Deferred Decisions, and Risks

| **Status**  | **Item**               | **Decision**                                                              |
|-------------|------------------------|---------------------------------------------------------------------------|
| DECIDED     | Timeline persistence   | No dedicated timeline table in Story 4.1.                                 |
| DECIDED     | Canonical time         | UTC observed_at semantics; \[start,end).                                  |
| DECIDED     | Density source         | Existing band hourly/daily rollups.                                       |
| DECIDED     | Marker abstraction     | Source-independent TimelineEvent contract.                                |
| DECIDED     | Initial resolutions    | hour and day.                                                             |
| RECOMMENDED | Auto threshold         | Use hour through 14 days, day beyond 14 days; tune by profiling/UI needs. |
| DEFERRED    | Fine-grained density   | Minute/5-minute buckets from raw spots only if frontend needs them.       |
| DEFERRED    | Persisted anomalies    | Epic 5 owns anomaly storage and scoring.                                  |
| RISK        | Null-band observations | Not represented in band-rollup density.                                   |
| RISK        | Peak-marker threshold  | Needs product tuning to avoid noisy marker fields.                        |

# 13. Definition of Ready for Story 4.2

- TimelineBucket and TimelineEvent contracts are accepted.

- UTC half-open interval semantics are accepted as identical to replay.

- Hourly/daily rollups are accepted as the initial density source.

- No timeline-specific persistence migration is required.

- Auto-resolution policy is treated as configurable service behavior.

- Activity markers may ship before anomaly persistence by using the same
  event contract.

- The null-band density limitation is documented and consciously
  accepted or separately addressed.

# 14. Traceability to Supplied Artifacts

This design was derived from the supplied Phase 3 roadmap and the
backend repository snapshot. Repository artifacts inspected include:

- docs/architecture/Analytics_Aggregation_Schema.md

- docs/architecture/Replay_Architecture.md

- app/analytics/aggregation/models.py and queries.py

- app/replay/streaming/models.py, queries.py, source.py, and prefetch.py

- app/infrastructure/database/models.py

- migrations/versions/9601bd15dc66_add_analytics_aggregation_tables.py

- app/api/routes/statistics.py and shared API validation/dependencies

- tests for analytics aggregation/statistics and replay
  streaming/repositories

Roadmap anchor: Epic 4 / Story 4.1 requires timeline density buckets,
notable-activity event markers, and a documented timeline data contract;
Story 4.2 then implements GET /api/v1/timeline with zoom-aware
resolution, marker retrieval, and date-range queries.

# 15. Architect Handoff

Story 4.2 can proceed without a schema migration. Implement the timeline
as a thin application/read-model layer over analytics rollups, preserve
replay’s temporal rules, and keep markers composable. This keeps the
timeline lightweight now while leaving a clean socket for Epic 5
anomalies later. The result is a scrubber model that can span the full
history without hauling the entire observation universe through the API
like a radio telescope strapped to a shopping cart.
