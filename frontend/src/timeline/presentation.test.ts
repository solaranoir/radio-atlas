import { expect, it } from "vitest";
import { formatTimelineTime, formatWindowDuration } from "./presentation";
it("uses readable dates and UTC independently of the user's timezone", () => {
    expect(formatTimelineTime("2026-10-09T14:30:00Z")).toContain("Oct 9, 2026");
    expect(formatTimelineTime("2026-10-09T16:30:00+02:00")).toContain("14:30:00");
    expect(formatTimelineTime("2026-10-09T14:30:00Z", true)).toContain("14:30");
    expect(formatTimelineTime("2026-10-09T14:30:00Z", true)).not.toContain("2026");
});
it("describes the visible duration in sensible human units", () => {
    const start_time = "2026-10-09T00:00:00Z";
    expect(formatWindowDuration({ start_time, end_time: "2026-10-09T00:00:00.000001Z" })).toBe("Less than a second");
    expect(formatWindowDuration({ start_time, end_time: "2026-10-09T00:00:01Z" })).toBe("1 second");
    expect(formatWindowDuration({ start_time, end_time: "2026-10-09T00:30:00Z" })).toBe("30 minutes");
    expect(formatWindowDuration({ start_time, end_time: "2026-10-09T02:00:00Z" })).toBe("2 hours");
    expect(formatWindowDuration({ start_time, end_time: "2026-10-11T00:00:00Z" })).toBe("2 days");
});
