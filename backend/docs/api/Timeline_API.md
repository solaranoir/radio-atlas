# Timeline API

Phase 3 Story 4.2 implements `GET /api/v1/timeline`. The generated OpenAPI
document at `/openapi.json` includes query constraints and response models.
See the [design contract](../architecture/Timeline_Data_Model.md) for temporal,
coverage, and scrubbing semantics.

## Requests

```sh
curl 'http://localhost:8000/api/v1/timeline'
curl 'http://localhost:8000/api/v1/timeline?start_time=2026-09-01T00:00:00Z&end_time=2026-09-03T00:00:00Z&resolution=hour&max_buckets=48&event_limit=10'
```

Omit both timestamps to select full raw-observation history; otherwise provide
both with a timezone and a strictly increasing range. Offset timestamps are
converted to UTC. Ranges are inclusive at start and exclusive at end.

| Query | Default | Constraint |
| --- | --- | --- |
| `start_time`, `end_time` | null | Both or neither; aware RFC 3339 timestamps |
| `resolution` | auto | auto, minute, hour, day |
| `max_buckets` | 512 | 1–2048 |
| `include_events` | true | Boolean |
| `event_limit` | 100 | 1–500 |
| `event_cursor` | null | Opaque continuation, at most 1024 characters |

An explicit resolution is the minimum display width; long ranges still group
source units to meet the bucket cap. `bucket_seconds` reports the actual width.
The final bucket can be shorter. Every display interval is returned, including
zero counts. Normalization uses the largest visible count.

Minute data counts all raw spots. Hour/day data counts band-resolved spots from
rollups, with raw counts restricted to partial source boundaries. No per-bucket
queries are issued. Missing rollups cannot establish completeness, so their
`aggregation_status` remains `unknown`. Raw-only output uses `not_applicable`.
No new database migration, dependency, or configuration is required.

## Events and continuation

Activity peaks are informative interval markers, not anomaly classifications.
Strict neighbor maxima qualify if at least twice the visible median and at
least two observations. IDs include coverage, width, and interval boundaries.
Equal-count plateaus are excluded.

To continue, repeat the same bounds and all options with the returned
`next_event_cursor`. Continuations are bound to history metadata and density
counts. A changed range, options, or density snapshot yields HTTP 409; refresh
without a cursor. Cursors are positional read continuations, not authentication
credentials or authorization tokens.

Empty history with omitted bounds returns null range/width/source metadata,
empty arrays, and no cursor. Explicit ranges on empty history return zero
buckets. Refer to the design document for the complete JSON example.

| HTTP status | Meaning |
| --- | --- |
| 200 | Timeline returned |
| 400 | Invalid range, naive timestamp, or incompatible options |
| 409 | Invalid, incompatible, or stale marker cursor |
| 422 | Malformed query value or parameter outside declared limits |
| 500 | Source counts exceed the safe JSON integer range or response validation fails |

Errors follow `{"error":{"code":"...","message":"..."}}`; query validation
also provides details. The endpoint reads timeline state and does not seek,
play, or pause replay. The frontend integration remains Story 4.3.
