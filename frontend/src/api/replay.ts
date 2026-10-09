import type { TimelineRange } from "./timeline";
export interface ReplaySession extends TimelineRange {
    session_id: string;
    position: string;
    state: "paused" | "playing" | "completed";
    speed: number;
    created_at: string;
    updated_at: string;
}
export class ReplayRequestError extends Error {
    readonly status: number;
    constructor(status: number) {
        super(`Replay request failed (${status}). Try seeking again.`);
        this.status = status;
    }
}
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
async function requestSession(path: string, method: string, body: object, signal: AbortSignal): Promise<ReplaySession> {
    const response = await fetch(new URL(path, API_BASE_URL), {
        method, signal, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
    });
    if (!response.ok)
        throw new ReplayRequestError(response.status);
    return response.json() as Promise<ReplaySession>;
}
export function createReplaySession(range: TimelineRange, signal: AbortSignal): Promise<ReplaySession> {
    return requestSession("/api/v1/replay/sessions", "POST", range, signal);
}
export function seekReplaySession(sessionId: string, position: string, signal: AbortSignal): Promise<ReplaySession> {
    return requestSession(`/api/v1/replay/sessions/${encodeURIComponent(sessionId)}`, "PATCH", { action: "seek", position }, signal);
}
export function updateReplaySession(sessionId: string, action: "play" | "pause" | "speed", signal: AbortSignal, speed?: number): Promise<ReplaySession> {
    return requestSession(`/api/v1/replay/sessions/${encodeURIComponent(sessionId)}`, "PATCH", { action, ...(speed === undefined ? {} : { speed }) }, signal);
}
export function replayStreamUrl(sessionId: string): string {
    const url = new URL(`/api/v1/replay/sessions/${encodeURIComponent(sessionId)}/stream`, API_BASE_URL);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    return url.toString();
}
