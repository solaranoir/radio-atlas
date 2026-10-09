import { afterEach, expect, it, vi } from "vitest";
import { createReplaySession, ReplayRequestError, seekReplaySession } from "./replay";
import { fetchTimeline } from "./timeline";
afterEach(() => vi.unstubAllGlobals());
it("preserves exact UTC range, marker cursor and cancellation signal", async () => {
    const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ schema_version: 1 }) });
    vi.stubGlobal("fetch", fetch);
    const signal = new AbortController().signal;
    await fetchTimeline({ start_time: "2026-01-01T00:00:00.000001Z", end_time: "2026-01-02T00:00:00Z" }, signal, "cursor");
    const url = fetch.mock.calls[0][0] as URL;
    expect(url.pathname).toBe("/api/v1/timeline");
    expect(url.searchParams.get("start_time")).toBe("2026-01-01T00:00:00.000001Z");
    expect(url.searchParams.get("event_cursor")).toBe("cursor");
    expect(fetch.mock.calls[0][1].signal).toBe(signal);
});
it("omits bounds for full history and surfaces backend failures", async () => {
    const fetch = vi.fn().mockResolvedValue({ ok: false, status: 409 });
    vi.stubGlobal("fetch", fetch);
    await expect(fetchTimeline(null, new AbortController().signal)).rejects.toThrow("409");
    expect((fetch.mock.calls[0][0] as URL).searchParams.has("start_time")).toBe(false);
});
it("creates sessions and sends semantic seek actions with microsecond precision", async () => {
    const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ session_id: "session" }) });
    vi.stubGlobal("fetch", fetch);
    const signal = new AbortController().signal;
    const range = { start_time: "2026-01-01T00:00:00Z", end_time: "2026-01-02T00:00:00Z" };
    await createReplaySession(range, signal);
    await seekReplaySession("session", "2026-01-01T00:00:00.000001Z", signal);
    expect(fetch.mock.calls[0][1].method).toBe("POST");
    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual(range);
    expect(fetch.mock.calls[1][1].method).toBe("PATCH");
    expect(JSON.parse(fetch.mock.calls[1][1].body)).toEqual({ action: "seek", position: "2026-01-01T00:00:00.000001Z" });
    fetch.mockResolvedValueOnce({ ok: false, status: 404 });
    await expect(seekReplaySession("session", range.end_time, signal)).rejects.toBeInstanceOf(ReplayRequestError);
});
