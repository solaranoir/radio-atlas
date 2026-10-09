import type { TimelineRange } from "../api/timeline";
import { timestampMicroseconds } from "./time";
export function formatTimelineTime(timestamp: string, compact = false): string {
    return new Intl.DateTimeFormat("en-US", {
        timeZone: "UTC", month: "short", day: "numeric", ...(compact ? {} : { year: "numeric" as const }),
        hour: "2-digit", minute: "2-digit", ...(compact ? {} : { second: "2-digit" as const }), hourCycle: "h23",
    }).format(new Date(timestamp));
}
export function formatWindowDuration(range: TimelineRange): string {
    const seconds = Number(timestampMicroseconds(range.end_time) - timestampMicroseconds(range.start_time)) / 1000000;
    if (seconds < 1)
        return "Less than a second";
    const units: [
        number,
        string
    ][] = [[86400, "day"], [3600, "hour"], [60, "minute"], [1, "second"]];
    const [size, label] = units.find(([size]) => seconds >= size)!;
    const value = Math.round(seconds / size * 10) / 10;
    return `${value.toLocaleString()} ${label}${value === 1 ? "" : "s"}`;
}
