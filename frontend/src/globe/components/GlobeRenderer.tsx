import { useMemo, useRef } from "react";

import { filterObservations } from "../filters/filterObservations";
import { useAnomalies } from "../hooks/useAnomalies";
import { useGlobeRenderer } from "../hooks/useGlobeRenderer";
import { useReducedMotionPreference } from "../hooks/useReducedMotionPreference";
import { useObservations } from "../hooks/useObservations";
import { useSolarWeather } from "../hooks/useSolarWeather";
import type { GlobeLayerId } from "../layers/globeLayer";
import type { RenderingPerformanceSnapshot } from "../rendering/RenderingPerformanceMonitor";
import { adaptObservationsForVisualization } from "../utilities/observationVisualizationAdapter";
import { useGlobeStore } from "../state/globeStore";
import { FilterPanel } from "./FilterPanel";
import { GlobeLayout } from "./GlobeLayout";
import { InformationPanel } from "./InformationPanel";
import { LayerControls } from "./LayerControls";
import { MotionPreferenceControl } from "./MotionPreferenceControl";

export function GlobeRenderer() {
    const containerRef = useRef<HTMLDivElement | null>(null);

    const reducedMotion = useReducedMotionPreference();

    const { snapshot: solarWeather } = useSolarWeather();

    const filters = useGlobeStore((state) => state.filters);

    const setFilters = useGlobeStore((state) => state.setFilters);

    const selection = useGlobeStore((state) => state.selection);

    const setSelection = useGlobeStore((state) => state.setSelection);

    const setCamera = useGlobeStore((state) => state.setCamera);

    const setLayerActive = useGlobeStore((state) => state.setLayerActive);

    const handleLayerVisibilityChange = (
        layerId: GlobeLayerId,
        visible: boolean,
    ) => {
        setLayerVisible(layerId, visible);

        setLayerActive(layerId, visible);
    };

    const handleGlobeKeyDown = (
        event: React.KeyboardEvent<HTMLDivElement>,
    ): void => {
        const rotationStep = Math.PI / 36;

        switch (event.key) {
            case "ArrowLeft":
                event.preventDefault();
                rotateCamera(-rotationStep, 0);
                break;

            case "ArrowRight":
                event.preventDefault();
                rotateCamera(rotationStep, 0);
                break;

            case "ArrowUp":
                event.preventDefault();
                rotateCamera(0, -rotationStep);
                break;

            case "ArrowDown":
                event.preventDefault();
                rotateCamera(0, rotationStep);
                break;

            case "+":
            case "=":
                event.preventDefault();
                zoomCamera(0.9);
                break;

            case "-":
                event.preventDefault();
                zoomCamera(1.1);
                break;

            case "Enter":
                event.preventDefault();
                selectAtViewportCenter();
                break;

            case "Escape":
                event.preventDefault();
                clearCurrentSelection();
                break;
        }
    };

    const { observations } = useObservations();

    const filteredObservations = useMemo(
        () => filterObservations(observations, filters),
        [observations, filters],
    );

    const anomalies = useAnomalies(filteredObservations);

    const observationVisualization = useMemo(
        () => adaptObservationsForVisualization(filteredObservations),
        [filteredObservations],
    );

    const handlePerformanceSnapshot = (
        snapshot: RenderingPerformanceSnapshot,
    ): void => {
        if (!import.meta.env.DEV) {
            return;
        }

        console.table(snapshot);
    };

    const {
        resetCamera,
        setLayerVisible,
        rotateCamera,
        zoomCamera,
        selectAtViewportCenter,
        clearCurrentSelection,
    } = useGlobeRenderer(
        containerRef,
        solarWeather,
        anomalies,
        observationVisualization,
        selection,
        setSelection,
        setCamera,
        handlePerformanceSnapshot,
        reducedMotion,
    );

    return (
        <GlobeLayout
            header={
                <div className="app-brand">
                    <div className="app-brand__title">SolaraSphere</div>

                    <div className="app-brand__subtitle">Radio Atlas</div>
                </div>
            }
            sidebar={
                <>
                    <section className="control-section">
                        <div className="control-section__heading">
                            Navigation
                        </div>

                        <button
                            type="button"
                            className="secondary-button"
                            onClick={resetCamera}
                        >
                            Reset camera
                        </button>
                    </section>

                    <section className="control-section">
                        <MotionPreferenceControl />
                    </section>
                    <section className="control-section">
                        <FilterPanel filters={filters} onChange={setFilters} />
                    </section>

                    <section className="control-section">
                        <LayerControls
                            onVisibilityChange={handleLayerVisibilityChange}
                        />
                    </section>
                </>
            }
            workspace={
                <div
                    ref={containerRef}
                    className="globe-container"
                    tabIndex={0}
                    role="application"
                    aria-label="Interactive radio weather globe"
                    onKeyDown={handleGlobeKeyDown}
                />
            }
            rightPanel={
                <InformationPanel
                    selection={selection}
                    observationCount={filteredObservations.length}
                    anomalyCount={anomalies.length}
                />
            }
            bottomPanel={
                <div className="activity-panel">
                    <h2>Activity</h2>

                    <div className="activity-panel__stats">
                        <span>
                            <strong>{filteredObservations.length}</strong> of{" "}
                            {observations.length} observations
                        </span>

                        <span>
                            <strong>{anomalies.length}</strong> anomalies
                        </span>
                    </div>
                </div>
            }
        />
    );
}
