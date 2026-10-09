export interface TimelineRange {
    start_time: string;
    end_time: string;
}
export interface TimelineBucket extends TimelineRange {
    observation_count: number;
    normalized_density: number;
}
export interface TimelineEvent {
    id: string;
    source: string;
    event_type: string;
    start_time: string;
    end_time: string | null;
    severity: "info" | "low" | "medium" | "high";
    label: string;
    observation_count: number | null;
    metadata: Record<string, unknown>;
}
export interface TimelineResponse {
    schema_version: 1;
    generated_at: string;
    history: {
        start_time: string | null;
        end_time: string | null;
    };
    start_time: string | null;
    end_time: string | null;
    source_resolution: "minute" | "hour" | "day" | null;
    bucket_seconds: number | null;
    density_coverage: "all_observations" | "band_resolved_observations" | null;
    aggregation_status: "unknown" | "not_applicable";
    buckets: TimelineBucket[];
    events: TimelineEvent[];
    next_event_cursor: string | null;
}
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
export async function fetchTimeline(range: TimelineRange | null, signal: AbortSignal, cursor: string | null = null): Promise<TimelineResponse> {
    const url = new URL("/api/v1/timeline", API_BASE_URL);
    url.searchParams.set("max_buckets", "128");
    url.searchParams.set("event_limit", "100");
    if (range) {
        url.searchParams.set("start_time", range.start_time);
        url.searchParams.set("end_time", range.end_time);
    }
    if (cursor)
        url.searchParams.set("event_cursor", cursor);
    const response = await fetch(url, { signal });
    if (!response.ok)
        throw new Error(`Timeline request failed (${response.status}). Refresh and try again.`);
    return response.json() as Promise<TimelineResponse>;
}
