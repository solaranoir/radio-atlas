import { useCallback, useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { formatTimelineTime, formatWindowDuration } from "./presentation";
import { positionAt, positionFraction, SLIDER_STEPS, timestampMicroseconds, zoomRange } from "./time";
import { useTimeline } from "./useTimeline";
import "./timeline.css";
export function TimelineScrubber() {
    const timeline = useTimeline();
    const [expanded, setExpanded] = useState(false);
    const dialog = useRef<HTMLDialogElement | null>(null);
    const expandButton = useRef<HTMLButtonElement | null>(null);
    const labelId = useId();
    const descriptionId = useId();
    const range = timeline.visible;
    const position = timeline.position;
    const data = timeline.data;
    const history = timeline.history;
    const restoreFocus = useCallback(() => expandButton.current?.focus(), []);
    useEffect(() => {
        if (!expanded || !dialog.current)
            return;
        const element = dialog.current;
        const previousOverflow = document.body.style.overflow;
        element.showModal();
        document.body.style.overflow = "hidden";
        return () => {
            element.close();
            document.body.style.overflow = previousOverflow;
            restoreFocus();
        };
    }, [expanded, restoreFocus]);
    const zoom = (direction: "in" | "out") => {
        if (!range || !history || !position)
            return;
        const center = timeline.replay ? position : positionAt(range, 5000);
        timeline.changeRange(zoomRange(range, history, center, direction));
    };
    const chooseMarker = (target: string) => {
        if (!history)
            return;
        const value = timestampMicroseconds(target);
        timeline.seek(value < timestampMicroseconds(history.start_time) ? history.start_time
            : value > timestampMicroseconds(history.end_time) ? history.end_time : target);
    };
    const isFullHistory = range && history && timestampMicroseconds(range.start_time) === timestampMicroseconds(history.start_time) && timestampMicroseconds(range.end_time) === timestampMicroseconds(history.end_time);
    const selectedBucket = data?.buckets.find((bucket) => position && timestampMicroseconds(position) >= timestampMicroseconds(bucket.start_time) && timestampMicroseconds(position) < timestampMicroseconds(bucket.end_time));
    const peakCount = Math.max(0, ...(data?.buckets.map((bucket) => bucket.observation_count) ?? []));
    const panel = (<section className="timeline" aria-labelledby={labelId}>
            <header className="timeline__heading">
                <div><h2 id={labelId}>Explore radio activity</h2><p>Find a time to replay</p></div>
                <button ref={expanded ? undefined : expandButton} className="secondary-button timeline__fullscreen" type="button" aria-label={expanded ? "Close full-screen timeline" : "Expand timeline"} title={expanded ? "Exit full screen" : "View full screen"} onClick={() => setExpanded(!expanded)}>
                    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <path d={expanded ? "M4 9h5V4M15 4v5h5M20 15h-5v5M9 20v-5H4" : "M9 4H4v5M15 4h5v5M20 15v5h-5M4 15v5h5"}/>
                    </svg>
                </button>
            </header>
            {timeline.loading && <p role="status">Loading historical activity…</p>}
            {timeline.error && <p role="alert">{timeline.error}</p>}
            {data && !range && <p>No historical observations are available yet.</p>}
            {range && position && data && (<>
                    <div className="timeline__window">
                        <div><span className="timeline__eyebrow">Visible time range · UTC</span><p><strong>{formatTimelineTime(range.start_time)} — {formatTimelineTime(range.end_time)}</strong></p><p>{formatWindowDuration(range)} shown</p></div>
                        <div className="timeline__actions">
                            <button className="secondary-button" type="button" title="Halve the time range to see more detail" disabled={!history || timestampMicroseconds(range.end_time) - timestampMicroseconds(range.start_time) <= 1n} onClick={() => zoom("in")}>Show less time</button>
                            <button className="secondary-button" type="button" title="Double the time range to see more history" disabled={!history || Boolean(isFullHistory)} onClick={() => zoom("out")}>Show more time</button>
                            <button className="secondary-button" type="button" disabled={!history || Boolean(isFullHistory)} onClick={() => timeline.changeRange(null)}>All history</button>
                            <button className="secondary-button" type="button" onClick={timeline.refresh}>Refresh timeline</button>
                        </div>
                    </div>
                    <figure className="timeline__figure">
                        <figcaption><strong>Reception reports over time</strong><span>Highest interval: {peakCount.toLocaleString()} reports</span></figcaption>
                        <div className="timeline__density" aria-hidden="true">
                            <svg viewBox="0 0 1000 100" preserveAspectRatio="none">
                                {data.buckets.map((bucket) => {
                const start = positionFraction(range, bucket.start_time) * 1000;
                const width = positionFraction(range, bucket.end_time) * 1000 - start;
                return <rect key={bucket.start_time} x={start} width={width} y={100 - bucket.normalized_density * 100} height={bucket.normalized_density * 100}/>;
            })}
                                {data.events.map((event) => <line key={`${event.source}:${event.id}`} className="timeline__marker" x1={positionFraction(range, event.start_time) * 1000} x2={positionFraction(range, event.start_time) * 1000} y1="0" y2="100"/>)}
                                <line className="timeline__cursor" x1={positionFraction(range, position) * 1000} x2={positionFraction(range, position) * 1000} y1="0" y2="100"/>
                            </svg>
                        </div>
                        <div className="timeline__axis" aria-label="Time axis in UTC">
                            {[0, 2500, 5000, 7500, 10000].map((step) => <time key={step} dateTime={positionAt(range, step)}>{formatTimelineTime(positionAt(range, step), true)}</time>)}
                        </div>
                        <div className="timeline__legend"><span><i className="timeline__swatch"/>Reports</span><span><i className="timeline__swatch timeline__swatch--event"/>Busy periods</span><span><i className="timeline__swatch timeline__swatch--position"/>Selected time</span></div>
                    </figure>
                    <div className="timeline__selection">
                        <div><span className="timeline__eyebrow">Selected replay time · UTC</span><p><strong><time dateTime={position}>{formatTimelineTime(position)}</time></strong></p></div>
                        <p>{selectedBucket ? `${selectedBucket.observation_count.toLocaleString()} reports in this interval` : "End of the selected range"}</p>
                    </div>
                    <label htmlFor={`${labelId}-position`}>Choose a replay time</label>
                    <input id={`${labelId}-position`} type="range" min="0" max={SLIDER_STEPS} step="1" value={Math.round(positionFraction(range, position) * SLIDER_STEPS)} aria-valuetext={`${formatTimelineTime(position)} UTC`} aria-describedby={descriptionId} onChange={(event) => timeline.seek(positionAt(range, Number(event.target.value)))}/>
                    <div className="timeline__actions" aria-label="Replay controls">
                        <button className="secondary-button" type="button" disabled={timeline.controlling} onClick={() => timeline.seek(range.start_time)}>Beginning</button>
                        <button className="secondary-button" type="button" disabled={!timeline.replay || timeline.seeking || timeline.controlling || !timeline.streamConnected || timeline.replay.state === "completed"} onClick={() => void timeline.control(timeline.replay?.state === "playing" ? "pause" : "play")}>{timeline.replay?.state === "playing" ? "Pause" : "Play"}</button>
                        <button className="secondary-button" type="button" disabled={timeline.controlling} onClick={() => timeline.seek(range.end_time)}>End</button>
                        <label htmlFor={`${labelId}-speed`}>Speed</label>
                        <select id={`${labelId}-speed`} value={timeline.replay?.speed ?? 1} disabled={!timeline.replay || timeline.seeking || timeline.controlling} onChange={(event) => void timeline.control("speed", Number(event.target.value))}>
                            <option value={1}>Real time</option><option value={60}>1 minute / second</option><option value={3600}>1 hour / second</option>
                        </select>
                    </div>
                    <p id={descriptionId} className="timeline__guidance">Drag the slider or use arrow keys to choose when replay starts. Home selects the beginning; End selects the end. Then press Play to advance the timeline.</p>
                    <p role="status" aria-live="polite">{timeline.seeking ? "Setting replay time…" : timeline.replay ? `${timeline.replay.state === "playing" ? "Playing" : "Replay time set to"} ${formatTimelineTime(timeline.replay.position)} UTC${timeline.replay.state === "completed" ? " · end of history" : ""}` : "Choose a time to enable Play."}</p>
                    {timeline.seekError && <p role="alert">{timeline.seekError} <button className="secondary-button" type="button" onClick={() => timeline.seek(position)}>Retry seek</button></p>}
                    {timeline.replay && !timeline.streamConnected && <p role="status">Connecting replay… Play will be available when connected.</p>}
                    <p className="timeline__notice">Play advances the timeline clock. The globe still shows live activity; historical globe playback is not connected yet.</p>
                    <section className="timeline__events" aria-label="Busy periods">
                        <h3>Busy periods</h3><p>Select a period to set the replay time.</p>
                        {data.events.length ? <ul>{data.events.map((event) => <li key={`${event.source}:${event.id}`}><button className="secondary-button" type="button" onClick={() => chooseMarker(event.start_time)}><strong>{formatTimelineTime(event.start_time)} UTC</strong><span>{event.label}{event.observation_count !== null ? ` · ${event.observation_count.toLocaleString()} reports` : ""}</span></button></li>)}</ul> : <p>No unusually busy periods in this time range.</p>}
                        {data.next_event_cursor && <button className="secondary-button" type="button" disabled={timeline.markersLoading} onClick={() => void timeline.moreMarkers()}>{timeline.markersLoading ? "Loading periods…" : "Load more periods"}</button>}
                        {timeline.markerError && <p role="alert">{timeline.markerError} Refresh the timeline to try again.</p>}
                    </section>
                    <details><summary>Report counts by time</summary><div className="timeline__table-scroll"><table><caption>Reception reports in each interval (UTC)</caption><thead><tr><th scope="col">From</th><th scope="col">To</th><th scope="col">Reports</th></tr></thead><tbody>{data.buckets.map((bucket) => <tr key={bucket.start_time}><td>{formatTimelineTime(bucket.start_time)}</td><td>{formatTimelineTime(bucket.end_time)}</td><td>{bucket.observation_count.toLocaleString()}</td></tr>)}</tbody></table></div></details>
                    <p className="timeline__footnote">{data.density_coverage === "band_resolved_observations" ? "Only reports with an identified radio band are counted." : "All reception reports are counted."} {data.aggregation_status === "unknown" && "Historical totals may still be updating."}</p>
                </>)}
            {!range && <button className="secondary-button" type="button" disabled={timeline.loading} onClick={timeline.refresh}>Refresh timeline</button>}
        </section>);
    return expanded ? createPortal(<dialog ref={dialog} className="timeline-dialog" aria-labelledby={labelId} onCancel={(event) => { event.preventDefault(); setExpanded(false); }}>{panel}</dialog>, document.body) : panel;
}
