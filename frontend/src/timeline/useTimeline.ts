import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createReplaySession, ReplayRequestError, replayStreamUrl, seekReplaySession, updateReplaySession, type ReplaySession } from "../api/replay";
import { fetchTimeline, type TimelineRange, type TimelineResponse } from "../api/timeline";
import { timestampMicroseconds } from "./time";
export function useTimeline() {
    const [range, setRange] = useState<TimelineRange | null>(null);
    const [revision, setRevision] = useState(0);
    const [result, setResult] = useState<{
        data: TimelineResponse | null;
        loading: boolean;
        error: string | null;
    }>({ data: null, loading: true, error: null });
    const [position, setPosition] = useState<string | null>(null);
    const [replay, setReplay] = useState<ReplaySession | null>(null);
    const [seekError, setSeekError] = useState<string | null>(null);
    const [seeking, setSeeking] = useState(false);
    const [controlling, setControlling] = useState(false);
    const [stream, setStream] = useState<{
        id: string;
        connected: boolean;
    } | null>(null);
    const controlBusy = useRef(false);
    const [markersLoading, setMarkersLoading] = useState(false);
    const [markerError, setMarkerError] = useState<string | null>(null);
    const markerController = useRef<AbortController | null>(null);
    const session = useRef<ReplaySession | null>(null);
    const queued = useRef<{
        position: string;
        history: TimelineRange;
    } | null>(null);
    const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const busy = useRef(false);
    const lifetime = useRef<AbortController | null>(null);
    const replayId = replay?.session_id;
    useEffect(() => {
        if (!replayId)
            return;
        let disposed = false;
        let socket: WebSocket;
        let retry: ReturnType<typeof setTimeout> | undefined;
        const connect = () => {
            socket = new WebSocket(replayStreamUrl(replayId));
            socket.onopen = () => { if (!disposed)
                setStream({ id: replayId, connected: true }); };
            socket.onmessage = (message) => {
                if (disposed || busy.current || queued.current || controlBusy.current)
                    return;
                try {
                    const frame = JSON.parse(String(message.data)) as {
                        session_id?: string;
                        position?: string;
                        state?: string;
                    };
                    if (frame.session_id !== replayId || !frame.position || !["paused", "playing", "completed"].includes(frame.state ?? "") || !session.current)
                        return;
                    const value = timestampMicroseconds(frame.position);
                    if (value < timestampMicroseconds(session.current.start_time) || value > timestampMicroseconds(session.current.end_time))
                        return;
                    const updated = { ...session.current, position: frame.position, state: frame.state as ReplaySession["state"] };
                    session.current = updated;
                    setReplay(updated);
                    setPosition(updated.position);
                }
                catch { /* Ignore invalid stream messages; keep the confirmed replay position. */ }
            };
            socket.onclose = (event) => {
                if (!disposed) {
                    setStream({ id: replayId, connected: false });
                    if (event?.code === 1008) {
                        setSeekError("Replay expired. Choose a time to reconnect.");
                        return;
                    }
                    retry = setTimeout(connect, 2000);
                }
            };
            socket.onerror = () => socket.close();
        };
        connect();
        return () => { disposed = true; if (retry)
            clearTimeout(retry); socket.close(); };
    }, [replayId]);
    useEffect(() => {
        const controller = new AbortController();
        lifetime.current = controller;
        return () => {
            controller.abort();
            markerController.current?.abort();
            if (timer.current)
                clearTimeout(timer.current);
        };
    }, []);
    useEffect(() => {
        const controller = new AbortController();
        void fetchTimeline(range, controller.signal).then((data) => {
            if (!controller.signal.aborted)
                setResult({ data, loading: false, error: null });
        }).catch((error: unknown) => {
            if (!controller.signal.aborted)
                setResult({ data: null, loading: false, error: error instanceof Error ? error.message : "Timeline could not load." });
        });
        return () => controller.abort();
    }, [range, revision]);
    const history = useMemo(() => result.data?.history.start_time && result.data.history.end_time
        ? { start_time: result.data.history.start_time, end_time: result.data.history.end_time } : null, [result.data]);
    const visible = result.data?.start_time && result.data.end_time
        ? { start_time: result.data.start_time, end_time: result.data.end_time } : null;
    const changeRange = (next: TimelineRange | null) => {
        setResult({ data: null, loading: true, error: null });
        markerController.current?.abort();
        setMarkersLoading(false);
        setMarkerError(null);
        setRange(next);
        setRevision((value) => value + 1);
    };
    const seek = useCallback((target: string) => {
        if (!history || !lifetime.current)
            return;
        const bounded = timestampMicroseconds(target);
        if (bounded < timestampMicroseconds(history.start_time) || bounded > timestampMicroseconds(history.end_time))
            return;
        setPosition(target);
        setSeeking(true);
        setSeekError(null);
        queued.current = { position: target, history };
        if (timer.current)
            clearTimeout(timer.current);
        const controller = lifetime.current;
        const drain = () => {
            if (busy.current || controller.signal.aborted)
                return;
            if (controlBusy.current) {
                timer.current = setTimeout(drain, 150);
                return;
            }
            busy.current = true;
            setSeeking(true);
            void (async () => {
                try {
                    while (queued.current && !controller.signal.aborted) {
                        const { position: next, history: requestedHistory } = queued.current;
                        queued.current = null;
                        if (!session.current || timestampMicroseconds(next) < timestampMicroseconds(session.current.start_time) || timestampMicroseconds(next) > timestampMicroseconds(session.current.end_time)) {
                            session.current = await createReplaySession(requestedHistory, controller.signal);
                        }
                        let updated: ReplaySession;
                        try {
                            updated = await seekReplaySession(session.current.session_id, next, controller.signal);
                        }
                        catch (error) {
                            if (!(error instanceof ReplayRequestError) || error.status !== 404)
                                throw error;
                            session.current = await createReplaySession(requestedHistory, controller.signal);
                            updated = await seekReplaySession(session.current.session_id, next, controller.signal);
                        }
                        if (!controller.signal.aborted) {
                            session.current = updated;
                            setReplay(updated);
                            setSeekError(null);
                        }
                    }
                }
                catch (error) {
                    if (!controller.signal.aborted)
                        setSeekError(error instanceof Error ? error.message : "Replay seek failed.");
                }
                finally {
                    busy.current = false;
                    if (!controller.signal.aborted) {
                        setSeeking(false);
                        if (queued.current)
                            timer.current = setTimeout(drain, 150);
                    }
                }
            })();
        };
        timer.current = setTimeout(drain, 150);
    }, [history]);
    const control = async (action: "play" | "pause" | "speed", speed?: number) => {
        const current = session.current;
        const controller = lifetime.current;
        if (!current || !controller || busy.current || queued.current || controlBusy.current)
            return;
        controlBusy.current = true;
        setControlling(true);
        setSeekError(null);
        try {
            const updated = await updateReplaySession(current.session_id, action, controller.signal, speed);
            if (!controller.signal.aborted) {
                session.current = updated;
                setReplay(updated);
            }
        }
        catch (error) {
            if (!controller.signal.aborted)
                setSeekError(error instanceof Error ? error.message : "Playback control failed.");
        }
        finally {
            controlBusy.current = false;
            if (!controller.signal.aborted)
                setControlling(false);
        }
    };
    const moreMarkers = async () => {
        const data = result.data;
        if (markersLoading || !data?.next_event_cursor || !data.start_time || !data.end_time)
            return;
        markerController.current?.abort();
        const controller = new AbortController();
        markerController.current = controller;
        setMarkersLoading(true);
        setMarkerError(null);
        try {
            const page = await fetchTimeline({ start_time: data.start_time, end_time: data.end_time }, controller.signal, data.next_event_cursor);
            if (!controller.signal.aborted)
                setResult((current) => current.data === data ? { ...current, data: { ...data, events: [...data.events, ...page.events], next_event_cursor: page.next_event_cursor } } : current);
        }
        catch (error) {
            if (!controller.signal.aborted)
                setMarkerError(error instanceof Error ? error.message : "Markers could not load.");
        }
        finally {
            if (!controller.signal.aborted)
                setMarkersLoading(false);
        }
    };
    return { ...result, visible, history, position: position ?? visible?.start_time ?? null, replay,
        seeking, seekError, seek, control, controlling, streamConnected: stream?.id === replayId && stream?.connected === true, changeRange, refresh: () => changeRange(range),
        markersLoading, markerError, moreMarkers };
}
