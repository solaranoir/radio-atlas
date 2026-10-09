import { describe, expect, it } from "vitest";
import { formatMicroseconds, positionAt, positionFraction, timestampMicroseconds, zoomRange } from "./time";
const range = { start_time: "2026-01-01T00:00:00.000001Z", end_time: "2026-01-01T00:00:10.000001Z" };
describe("precise timeline coordinates", () => {
    it("preserves microseconds, offsets, and timestamps before the Unix epoch", () => {
        for (const value of [range.start_time, "1969-12-31T23:59:59.999999Z"]) {
            expect(formatMicroseconds(timestampMicroseconds(value))).toBe(value);
        }
        expect(timestampMicroseconds("2026-01-01T02:00:00.000001+02:00")).toBe(timestampMicroseconds(range.start_time));
    });
    it("maps exact endpoints, clamps positions and interpolates independently of density buckets", () => {
        expect(positionAt(range, -1)).toBe(range.start_time);
        expect(positionAt(range, 10001)).toBe(range.end_time);
        expect(positionAt(range, 5000)).toBe("2026-01-01T00:00:05.000001Z");
        expect(positionFraction(range, positionAt(range, 2500))).toBe(0.25);
        expect(positionFraction(range, "2025-01-01T00:00:00Z")).toBe(0);
        expect(positionFraction(range, "2027-01-01T00:00:00Z")).toBe(1);
    });
    it("handles histories shorter than a millisecond", () => {
        const tiny = { ...range, end_time: "2026-01-01T00:00:00.000002Z" };
        expect(positionAt(tiny, 10000)).toBe(tiny.end_time);
        expect(positionFraction(tiny, tiny.end_time)).toBe(1);
        expect(zoomRange(tiny, tiny, tiny.start_time, "in")).toEqual(tiny);
    });
    it("zooms around the position, clamps history boundaries and restores the full range", () => {
        const narrow = zoomRange(range, range, positionAt(range, 5000), "in");
        expect(narrow).toEqual({ start_time: "2026-01-01T00:00:02.500001Z", end_time: "2026-01-01T00:00:07.500001Z" });
        expect(zoomRange(narrow, range, range.end_time, "out")).toEqual(range);
        expect(zoomRange(range, range, range.start_time, "in").start_time).toBe(range.start_time);
    });
    it("rejects unsupported or invalid timestamps", () => {
        expect(() => timestampMicroseconds("no date")).toThrow();
        expect(() => timestampMicroseconds("2026-99-99T00:00:00Z")).toThrow();
        expect(positionFraction({ ...range, end_time: range.start_time }, range.start_time)).toBe(0);
    });
});
