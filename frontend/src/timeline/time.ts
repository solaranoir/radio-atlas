import type { TimelineRange } from "../api/timeline";
export const SLIDER_STEPS = 10000;
export function timestampMicroseconds(value: string): bigint {
    const match = /^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,6}))?(Z|[+-]\d{2}:\d{2})$/.exec(value);
    if (!match)
        throw new Error("Timeline contains an unsupported timestamp.");
    const milliseconds = Date.parse(match[1] + match[3]);
    if (!Number.isFinite(milliseconds))
        throw new Error("Timeline contains an invalid timestamp.");
    return BigInt(milliseconds) * 1000n + BigInt((match[2] ?? "").padEnd(6, "0"));
}
export function formatMicroseconds(value: bigint): string {
    const seconds = value >= 0n ? value / 1000000n : (value - 999999n) / 1000000n;
    const fraction = value - seconds * 1000000n;
    return new Date(Number(seconds * 1000n)).toISOString().replace(".000Z", `.${fraction.toString().padStart(6, "0")}Z`);
}
export function positionAt(range: TimelineRange, step: number): string {
    const start = timestampMicroseconds(range.start_time);
    const end = timestampMicroseconds(range.end_time);
    const clamped = BigInt(Math.round(Math.max(0, Math.min(SLIDER_STEPS, step))));
    if (clamped === 0n)
        return range.start_time;
    if (clamped === BigInt(SLIDER_STEPS))
        return range.end_time;
    return formatMicroseconds(start + (end - start) * clamped / BigInt(SLIDER_STEPS));
}
export function positionFraction(range: TimelineRange, position: string): number {
    const start = timestampMicroseconds(range.start_time);
    const duration = timestampMicroseconds(range.end_time) - start;
    if (duration <= 0n)
        return 0;
    const scaled = (timestampMicroseconds(position) - start) * BigInt(SLIDER_STEPS) / duration;
    return Math.max(0, Math.min(1, Number(scaled) / SLIDER_STEPS));
}
export function zoomRange(range: TimelineRange, history: TimelineRange, position: string, direction: "in" | "out"): TimelineRange {
    const lower = timestampMicroseconds(history.start_time);
    const upper = timestampMicroseconds(history.end_time);
    const span = timestampMicroseconds(range.end_time) - timestampMicroseconds(range.start_time);
    const desired = direction === "in" ? span / 2n : span * 2n;
    const width = desired < 1n ? 1n : desired > upper - lower ? upper - lower : desired;
    let start = timestampMicroseconds(position) - width / 2n;
    start = start < lower ? lower : start;
    start = start + width > upper ? upper - width : start;
    return { start_time: formatMicroseconds(start), end_time: formatMicroseconds(start + width) };
}
