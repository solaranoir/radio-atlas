import type { ReplaySession } from "../api/replay";
import type { TimelineResponse } from "../api/timeline";
export class ReplaySocketFixture {
    static instances: ReplaySocketFixture[] = [];
    onopen: (() => void) | null = null;
    onmessage: ((event: {
        data: string;
    }) => void) | null = null;
    onclose: (() => void) | null = null;
    onerror: (() => void) | null = null;
    constructor() {
        ReplaySocketFixture.instances.push(this);
        queueMicrotask(() => this.onopen?.());
    }
    close() { this.onclose?.(); }
}
export const timelineFixture: TimelineResponse = {
    schema_version: 1, generated_at: "2026-01-02T00:00:00Z",
    history: { start_time: "2026-01-01T00:00:00Z", end_time: "2026-01-01T02:00:00.000001Z" },
    start_time: "2026-01-01T00:00:00Z", end_time: "2026-01-01T02:00:00.000001Z",
    source_resolution: "hour", bucket_seconds: 3600, density_coverage: "band_resolved_observations",
    aggregation_status: "unknown", next_event_cursor: null,
    buckets: [{ start_time: "2026-01-01T00:00:00Z", end_time: "2026-01-01T01:00:00Z", observation_count: 4, normalized_density: 1 }],
    events: [{ id: "peak", source: "timeline_activity", event_type: "activity_peak", label: "Activity peak", severity: "info", start_time: "2026-01-01T00:00:00Z", end_time: "2026-01-01T01:00:00Z", observation_count: 4, metadata: {} }],
};
export const replayFixture: ReplaySession = {
    session_id: "session", start_time: "2026-01-01T00:00:00Z", end_time: "2026-01-01T02:00:00.000001Z",
    position: "2026-01-01T00:00:00Z", state: "paused", speed: 1,
    created_at: "2026-01-02T00:00:00Z", updated_at: "2026-01-02T00:00:00Z",
};
