# Timeline Contract Test Plan

Phase 3 Story 4.1 is a design story. The following cases define verification
for implementation in Stories 4.2–4.4; they are not tests already executed.
Use deterministic synthetic UTC observations and disposable PostgreSQL in
Docker. No live providers are needed.

## Resolution and full history

For a 36,525-day range and `max_buckets = 512`, auto chooses daily input.
The width is `ceil(36,525 / 512) = 72 days` and the result contains
`ceil(36,525 / 72) = 508` buckets. The last bucket is clipped. Daily-only
output without grouping would instead produce 36,525 buckets and violate
the contract. Replay can still seek to any microsecond within that range.

Test widths at minute/hour/day thresholds, one microsecond over each
threshold, explicit resolution, `max_buckets = 1`, partial final buckets,
and 100-year ranges. Assert count never exceeds the requested cap, boundaries
are contiguous, and bucket coverage equals the requested interval exactly.

## Counts and coverage

- Seed spots exactly at start, intermediate boundary, and end. Start and
  intermediate observations occur once; end is excluded.
- Seed multiple bands/modes and sum counts once per eligible spot.
- Seed unresolved bands: minute/raw output includes them; rollup output
  excludes them consistently, including partial boundary queries.
- Seed source buckets crossing display boundaries. Compare partial edges
  with exact raw counts, without duplication or whole-bucket overcounting.
- Seed all-zero, isolated, and uneven counts. Verify normalization stays
  finite and within [0, 1], with zero for an all-zero response.
- Missing rollups retain `aggregation_status = unknown`; test late arrivals
  followed by refresh without interpreting zero fill as proven completeness.
- Verify global bounds retain unresolved-band and latest observations;
  omitted bounds on empty history return null metadata and empty arrays.

## Markers and limits

- Counts `[0, 4, 0]` produce one informative peak; `[0, 1, 0]` does not.
- Equal-count plateaus have no strict local peak. Test first and last peaks.
- Point events at end are excluded; intervals crossing start are included
  with original boundaries. Neighboring windows must not relabel events.
- Check stable IDs, source-aware deduplication, chronological ordering,
  marker caps, and continuation without silent truncation.
- Reject a cursor reused for a different range/width/source snapshot.
- Validate timestamp offsets, naive inputs, reversed bounds, invalid limits,
  oversized metadata/labels, unsafe integer counts, and non-finite densities.
- A future anomaly provider can add an event without changing bucket fields.

## Replay synchronization

Zoom changes bucket size without changing replay position. Scrub using pointer
and keyboard to arbitrary instants, including subsecond values, and assert
the existing seek API receives the exact UTC target within session bounds.
Seek at session end produces `completed`; paused seek remains paused and
playing seek remains playing. Test stale timeline responses during rapid
zooming, localized timestamps around DST, and replay ranges smaller than the
visible timeline range.

## Verification record

Story 4.1 changes documentation only. Check Markdown formatting, example JSON,
integer bucket-cap calculations, local links, and whitespace before handoff.
No runtime timeline tests or endpoint implementation are claimed by this plan.
