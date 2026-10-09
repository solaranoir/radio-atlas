// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createReplaySession, updateReplaySession, seekReplaySession } from "../api/replay";
import { fetchTimeline } from "../api/timeline";
import { TimelineScrubber } from "./TimelineScrubber";
import { ReplaySocketFixture, replayFixture, timelineFixture } from "./testFixtures";
vi.mock("../api/timeline", () => ({ fetchTimeline: vi.fn() }));
vi.mock("../api/replay", async (original) => {
    const actual = await original<typeof import("../api/replay")>();
    return { ...actual, createReplaySession: vi.fn(), seekReplaySession: vi.fn(), updateReplaySession: vi.fn() };
});
beforeEach(() => {
    ReplaySocketFixture.instances = [];
    vi.stubGlobal("WebSocket", ReplaySocketFixture);
    vi.mocked(updateReplaySession).mockImplementation(async (_, action, _signal, speed) => ({ ...replayFixture, state: action === "play" ? "playing" : "paused", speed: speed ?? 1 }));
    Object.defineProperty(HTMLDialogElement.prototype, "showModal", { configurable: true, value: vi.fn(function (this: HTMLDialogElement) { this.setAttribute("open", ""); }) });
    Object.defineProperty(HTMLDialogElement.prototype, "close", { configurable: true, value: vi.fn(function (this: HTMLDialogElement) { this.removeAttribute("open"); }) });
    vi.useFakeTimers();
    vi.mocked(fetchTimeline).mockResolvedValue(timelineFixture);
    vi.mocked(createReplaySession).mockResolvedValue(replayFixture);
    vi.mocked(seekReplaySession).mockImplementation(async (_, position) => ({ ...replayFixture, position }));
});
afterEach(() => { cleanup(); vi.useRealTimers(); vi.resetAllMocks(); vi.unstubAllGlobals(); vi.restoreAllMocks(); });
async function mount() {
    await act(async () => { render(<TimelineScrubber />); });
}
describe("timeline scrubber", () => {
    it("places markers and density proportionally within the visible time window", async () => {
        const end = "2026-01-01T02:00:00Z";
        vi.mocked(fetchTimeline).mockResolvedValue({
            ...timelineFixture, end_time: end,
            events: [0, 1, 2].map((hour) => ({ ...timelineFixture.events[0], id: `peak-${hour}`, start_time: `2026-01-01T0${hour}:00:00Z` })),
        });
        await mount();
        const markers = document.querySelectorAll(".timeline__marker");
        expect(Array.from(markers, (marker) => Number(marker.getAttribute("x1")))).toEqual([0, 500, 1000]);
        const bar = document.querySelector(".timeline__density rect");
        expect(bar?.getAttribute("x")).toBe("0");
        expect(bar?.getAttribute("width")).toBe("500");
        expect(bar?.getAttribute("height")).toBe("100");
        fireEvent.click(screen.getAllByRole("button", { name: /Activity peak/ })[1]);
        await act(async () => { await vi.advanceTimersByTimeAsync(150); });
        expect(seekReplaySession).toHaveBeenLastCalledWith("session", "2026-01-01T01:00:00Z", expect.any(AbortSignal));
        expect(document.querySelector(".timeline__cursor")?.getAttribute("x1")).toBe("500");
    });
    it("round-trips zoom ranges and keeps replay selection independent of zoom", async () => {
        vi.mocked(fetchTimeline).mockImplementation(async (range) => ({ ...timelineFixture, ...(range ?? {}) }));
        await mount();
        await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Show less time" })); });
        const narrow = vi.mocked(fetchTimeline).mock.calls[1][0];
        expect(narrow?.start_time).toBe("2026-01-01T00:30:00.000000Z");
        expect(narrow?.end_time).toBe("2026-01-01T01:30:00.000000Z");
        await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Show more time" })); });
        expect(vi.mocked(fetchTimeline).mock.calls[2][0]).toEqual({ start_time: "2026-01-01T00:00:00.000000Z", end_time: "2026-01-01T02:00:00.000000Z" });
        expect(createReplaySession).not.toHaveBeenCalled();
        expect(seekReplaySession).not.toHaveBeenCalled();
    });
    it("offers visible beginning/end, play/pause and speed controls", async () => {
        await mount();
        fireEvent.click(screen.getByRole("button", { name: "Beginning" }));
        await act(async () => { await vi.advanceTimersByTimeAsync(150); });
        expect(seekReplaySession).toHaveBeenLastCalledWith("session", timelineFixture.start_time, expect.any(AbortSignal));
        await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Play" })); });
        expect(updateReplaySession).toHaveBeenCalledWith("session", "play", expect.any(AbortSignal), undefined);
        expect(screen.getByRole("button", { name: "Pause" })).toBeTruthy();
        await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Pause" })); });
        await act(async () => { fireEvent.change(screen.getByRole("combobox", { name: "Speed" }), { target: { value: "3600" } }); });
        expect(updateReplaySession).toHaveBeenLastCalledWith("session", "speed", expect.any(AbortSignal), 3600);
        fireEvent.click(screen.getByRole("button", { name: "End" }));
        await act(async () => { await vi.advanceTimersByTimeAsync(150); });
        expect(seekReplaySession).toHaveBeenLastCalledWith("session", timelineFixture.end_time, expect.any(AbortSignal));
    });
    it("expands to a modal view and returns focus without losing the selected time", async () => {
        await mount();
        const expand = screen.getByRole("button", { name: "Expand timeline" });
        expand.focus();
        fireEvent.change(screen.getByRole("slider"), { target: { value: "5000" } });
        await act(async () => { await vi.advanceTimersByTimeAsync(150); });
        fireEvent.click(expand);
        expect(screen.getByRole("dialog", { name: "Explore radio activity" })).toBeTruthy();
        expect(screen.getByRole("slider").getAttribute("aria-valuetext")).toContain("01:00");
        expect(document.body.style.overflow).toBe("hidden");
        fireEvent.click(screen.getByRole("button", { name: "Close full-screen timeline" }));
        expect(screen.queryByRole("dialog")).toBeNull();
        expect(document.activeElement).toBe(screen.getByRole("button", { name: "Expand timeline" }));
        expect(document.body.style.overflow).not.toBe("hidden");
        expect(createReplaySession).toHaveBeenCalledTimes(1);
    });
    it("closes the expanded view with Escape's cancel event", async () => {
        await mount();
        fireEvent.click(screen.getByRole("button", { name: "Expand timeline" }));
        fireEvent(screen.getByRole("dialog"), new Event("cancel", { cancelable: true }));
        expect(screen.queryByRole("dialog")).toBeNull();
    });
    it("explains time selection and labels the graph without opening details", async () => {
        await mount();
        expect(screen.getByLabelText("Time axis in UTC").querySelectorAll("time")).toHaveLength(5);
        expect(screen.getByText(/Then press Play to advance the timeline/)).toBeTruthy();
        expect(screen.getAllByText(/^Reports$/).length).toBeGreaterThan(0);
        expect(screen.getByText(/historical globe playback is not connected/)).toBeTruthy();
        fireEvent.click(screen.getByText("Report counts by time"));
        expect(screen.getByRole("table")).toBeTruthy();
    });
    it("renders density, accessible timestamps, and marker actions", async () => {
        await mount();
        expect(screen.getByRole("slider", { name: "Choose a replay time" })).toBeTruthy();
        expect(screen.getByText(/4 reports in this interval/)).toBeTruthy();
        expect(screen.getByRole("button", { name: /Activity peak/ })).toBeTruthy();
    });
    it("debounces scrubbing and sends a precise terminal seek to a paused session", async () => {
        await mount();
        fireEvent.change(screen.getByRole("slider"), { target: { value: "5000" } });
        fireEvent.change(screen.getByRole("slider"), { target: { value: "10000" } });
        await act(async () => { await vi.advanceTimersByTimeAsync(150); });
        expect(createReplaySession).toHaveBeenCalledTimes(1);
        expect(seekReplaySession).toHaveBeenCalledTimes(1);
        expect(seekReplaySession).toHaveBeenCalledWith("session", timelineFixture.end_time, expect.any(AbortSignal));
    });
    it("zooming fetches a narrower range without seeking replay", async () => {
        await mount();
        await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Show less time" })); });
        expect(fetchTimeline).toHaveBeenCalledTimes(2);
        expect(vi.mocked(fetchTimeline).mock.calls[1][0]?.end_time).not.toBe(timelineFixture.end_time);
        expect(seekReplaySession).not.toHaveBeenCalled();
    });
    it("marker selection seeks and creation failures remain actionable", async () => {
        vi.mocked(createReplaySession).mockRejectedValueOnce(new Error("Backend unavailable"));
        await mount();
        fireEvent.click(screen.getByRole("button", { name: /Activity peak/ }));
        await act(async () => { await vi.advanceTimersByTimeAsync(150); });
        expect(screen.getByRole("alert").textContent).toContain("Backend unavailable");
        fireEvent.click(screen.getByRole("button", { name: "Retry seek" }));
        await act(async () => { await vi.advanceTimersByTimeAsync(150); });
        expect(seekReplaySession).toHaveBeenCalledTimes(1);
    });
    it("shows empty history and request errors without rendering a slider", async () => {
        vi.mocked(fetchTimeline).mockResolvedValueOnce({ ...timelineFixture, history: { start_time: null, end_time: null }, start_time: null, end_time: null, buckets: [], events: [] });
        await mount();
        expect(screen.queryByRole("slider")).toBeNull();
        expect(screen.getByText(/No historical observations/)).toBeTruthy();
        vi.mocked(fetchTimeline).mockRejectedValueOnce(new Error("Timeline unavailable"));
        await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Refresh timeline" })); });
        expect(screen.getByRole("alert").textContent).toContain("Timeline unavailable");
    });
});
