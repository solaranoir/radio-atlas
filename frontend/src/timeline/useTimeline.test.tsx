// @vitest-environment jsdom
import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { createReplaySession, updateReplaySession, ReplayRequestError, seekReplaySession, type ReplaySession } from "../api/replay";
import { fetchTimeline, type TimelineResponse } from "../api/timeline";
import { ReplaySocketFixture, replayFixture, timelineFixture } from "./testFixtures";
import { useTimeline } from "./useTimeline";
vi.mock("../api/timeline", () => ({ fetchTimeline: vi.fn() }));
vi.mock("../api/replay", async (original) => {
    const actual = await original<typeof import("../api/replay")>();
    return { ...actual, createReplaySession: vi.fn(), seekReplaySession: vi.fn(), updateReplaySession: vi.fn() };
});
beforeEach(() => {
    ReplaySocketFixture.instances = [];
    vi.stubGlobal("WebSocket", ReplaySocketFixture);
    vi.mocked(updateReplaySession).mockImplementation(async (_, action, _signal, speed) => ({ ...replayFixture, state: action === "play" ? "playing" : "paused", speed: speed ?? 1 }));
    vi.useFakeTimers();
    vi.mocked(fetchTimeline).mockResolvedValue(timelineFixture);
    vi.mocked(createReplaySession).mockResolvedValue(replayFixture);
    vi.mocked(seekReplaySession).mockImplementation(async (_, position) => ({ ...replayFixture, position }));
});
afterEach(() => { cleanup(); vi.useRealTimers(); vi.resetAllMocks(); vi.unstubAllGlobals(); });
it("ignores an obsolete timeline response after zoom", async () => {
    let resolve!: (value: TimelineResponse) => void;
    vi.mocked(fetchTimeline).mockReturnValueOnce(new Promise((done) => { resolve = done; }));
    const { result } = renderHook(useTimeline);
    const next = { start_time: "2026-01-01T01:00:00Z", end_time: timelineFixture.end_time! };
    await act(async () => { result.current.changeRange(next); });
    await act(async () => { resolve({ ...timelineFixture, events: [] }); });
    expect(result.current.data?.events).toHaveLength(1);
    expect(vi.mocked(fetchTimeline).mock.calls[0][1].aborted).toBe(true);
});
it("serializes in-flight seeks and applies the latest queued target", async () => {
    let resolve!: (value: ReplaySession) => void;
    vi.mocked(seekReplaySession).mockReturnValueOnce(new Promise((done) => { resolve = done; }));
    const { result } = renderHook(useTimeline);
    await act(async () => { });
    act(() => result.current.seek("2026-01-01T00:30:00Z"));
    await act(async () => { await vi.advanceTimersByTimeAsync(150); });
    act(() => result.current.seek("2026-01-01T01:00:00Z"));
    await act(async () => { await vi.advanceTimersByTimeAsync(150); });
    expect(seekReplaySession).toHaveBeenCalledTimes(1);
    await act(async () => { resolve({ ...replayFixture, position: "2026-01-01T00:30:00Z" }); });
    expect(seekReplaySession).toHaveBeenCalledTimes(2);
    expect(result.current.replay?.position).toBe("2026-01-01T01:00:00Z");
});
it("recreates an expired session once and retries the same seek", async () => {
    vi.mocked(seekReplaySession).mockRejectedValueOnce(new ReplayRequestError(404));
    const { result } = renderHook(useTimeline);
    await act(async () => { });
    act(() => result.current.seek("2026-01-01T00:30:00Z"));
    await act(async () => { await vi.advanceTimersByTimeAsync(150); });
    expect(createReplaySession).toHaveBeenCalledTimes(2);
    expect(seekReplaySession).toHaveBeenCalledTimes(2);
    expect(result.current.seekError).toBeNull();
});
it("loads marker continuation with unchanged query bounds", async () => {
    vi.mocked(fetchTimeline).mockResolvedValueOnce({ ...timelineFixture, next_event_cursor: "next" });
    const { result } = renderHook(useTimeline);
    await act(async () => { });
    await act(async () => { await result.current.moreMarkers(); });
    expect(vi.mocked(fetchTimeline).mock.calls[1][2]).toBe("next");
    expect(result.current.data?.events).toHaveLength(2);
});
it("cancels pending seeks when unmounted", async () => {
    const { result, unmount } = renderHook(useTimeline);
    await act(async () => { });
    act(() => result.current.seek("2026-01-01T00:30:00Z"));
    unmount();
    await vi.advanceTimersByTimeAsync(500);
    expect(createReplaySession).not.toHaveBeenCalled();
});
it("tracks replay clock frames and reconnects after losing the stream", async () => {
    const { result } = renderHook(useTimeline);
    await act(async () => { });
    act(() => result.current.seek("2026-01-01T00:30:00Z"));
    await act(async () => { await vi.advanceTimersByTimeAsync(150); });
    const socket = ReplaySocketFixture.instances[0];
    await act(async () => { await result.current.control("play"); });
    act(() => socket.onmessage?.({ data: JSON.stringify({ session_id: "session", position: "2026-01-01T00:31:00Z", state: "playing" }) }));
    expect(result.current.position).toBe("2026-01-01T00:31:00Z");
    act(() => socket.onmessage?.({ data: "invalid" }));
    expect(result.current.position).toBe("2026-01-01T00:31:00Z");
    act(() => socket.close());
    expect(result.current.streamConnected).toBe(false);
    await act(async () => { await vi.advanceTimersByTimeAsync(2000); });
    expect(ReplaySocketFixture.instances).toHaveLength(2);
    expect(result.current.streamConnected).toBe(true);
});
it("keeps the newest seek queued when an earlier request fails", async () => {
    let reject!: (value: Error) => void;
    vi.mocked(seekReplaySession).mockReturnValueOnce(new Promise((_, fail) => { reject = fail; }));
    const { result } = renderHook(useTimeline);
    await act(async () => { });
    act(() => result.current.seek("2026-01-01T00:30:00Z"));
    await act(async () => { await vi.advanceTimersByTimeAsync(150); });
    act(() => result.current.seek("2026-01-01T01:00:00Z"));
    await act(async () => { await vi.advanceTimersByTimeAsync(150); reject(new Error("Transient error")); });
    await act(async () => { await vi.advanceTimersByTimeAsync(150); });
    expect(result.current.replay?.position).toBe("2026-01-01T01:00:00Z");
});
it("ignores out-of-history seeks and reports marker continuation failures", async () => {
    vi.mocked(fetchTimeline).mockResolvedValueOnce({ ...timelineFixture, next_event_cursor: "next" });
    const { result } = renderHook(useTimeline);
    await act(async () => { });
    act(() => result.current.seek("2020-01-01T00:00:00Z"));
    await act(async () => { await vi.advanceTimersByTimeAsync(150); });
    expect(createReplaySession).not.toHaveBeenCalled();
    vi.mocked(fetchTimeline).mockRejectedValueOnce(new Error("Timeline request failed (409)"));
    await act(async () => { await result.current.moreMarkers(); });
    expect(result.current.markerError).toContain("409");
    expect(result.current.markersLoading).toBe(false);
});
it("aborts marker continuation and ignores its response when zoom changes", async () => {
    let resolve!: (value: TimelineResponse) => void;
    vi.mocked(fetchTimeline).mockResolvedValueOnce({ ...timelineFixture, next_event_cursor: "next" });
    const { result } = renderHook(useTimeline);
    await act(async () => { });
    vi.mocked(fetchTimeline).mockReturnValueOnce(new Promise((done) => { resolve = done; }));
    act(() => { void result.current.moreMarkers(); });
    const signal = vi.mocked(fetchTimeline).mock.calls[1][1];
    await act(async () => { result.current.changeRange(null); });
    await act(async () => { resolve(timelineFixture); });
    expect(signal.aborted).toBe(true);
    expect(result.current.data?.events).toHaveLength(1);
    expect(result.current.markersLoading).toBe(false);
});
