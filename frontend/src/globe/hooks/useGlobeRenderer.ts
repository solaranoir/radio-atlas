import { useCallback, useEffect, useRef, type RefObject } from "react";

import type { GlobeCameraState } from "../state/globeStore";
import type { Anomaly } from "../types/anomaly";
import type { GlobeLayerId } from "../layers/globeLayer";
import type { GlobeSelection } from "../types/globeSelection";
import type { SolarWeatherSnapshot } from "../types/solarWeather";
import { GlobeRenderingContext } from "../rendering/GlobeRenderingContext";
import type { RenderingPerformanceSnapshot } from "../rendering/RenderingPerformanceMonitor";
import type { ObservationVisualization } from "../utilities/observationVisualizationAdapter";

export function useGlobeRenderer(
    containerRef: RefObject<HTMLDivElement | null>,
    solarWeather: SolarWeatherSnapshot | null,
    anomalies: Anomaly[],
    observationVisualization: ObservationVisualization,
    selection: GlobeSelection,
    onSelectionChange?: (selection: GlobeSelection) => void,
    onCameraChange?: (camera: GlobeCameraState) => void,
    onPerformanceSnapshot?: (snapshot: RenderingPerformanceSnapshot) => void,
    reducedMotion = false,
): {
    resetCamera: () => void;
    rotateCamera: (horizontalRadians: number, verticalRadians: number) => void;
    zoomCamera: (scale: number) => void;
    selectAtViewportCenter: () => void;
    clearCurrentSelection: () => void;
    setLayerVisible: (id: GlobeLayerId, visible: boolean) => void;
} {
    const renderingContextRef = useRef<GlobeRenderingContext | null>(null);

    const layerVisibilityRef = useRef<Partial<Record<GlobeLayerId, boolean>>>(
        {},
    );

    const setLayerVisible = useCallback(
        (id: GlobeLayerId, visible: boolean): void => {
            layerVisibilityRef.current[id] = visible;

            renderingContextRef.current?.setLayerVisible(id, visible);
        },
        [],
    );

    useEffect(() => {
        renderingContextRef.current?.setSelectionChangeHandler(
            onSelectionChange ?? null,
        );
    }, [onSelectionChange]);

    useEffect(() => {
        renderingContextRef.current?.setCameraChangeHandler(
            onCameraChange ?? null,
        );
    }, [onCameraChange]);
    useEffect(() => {
        renderingContextRef.current?.setSelection(selection);
    }, [selection]);

    useEffect(() => {
        renderingContextRef.current?.setPerformanceSnapshotHandler(
            onPerformanceSnapshot ?? null,
        );
    }, [onPerformanceSnapshot]);

    useEffect(() => {
        if (containerRef.current === null) {
            return;
        }

        const container = containerRef.current;

        const renderingContext = new GlobeRenderingContext();

        renderingContextRef.current = renderingContext;

        renderingContext.setSelectionChangeHandler(onSelectionChange ?? null);

        for (const [id, visible] of Object.entries(
            layerVisibilityRef.current,
        )) {
            renderingContext.setLayerVisible(id as GlobeLayerId, visible);
        }

        renderingContext.mount(container);

        renderingContext.start();

        const resizeObserver = new ResizeObserver(() => {
            const { width, height } = container.getBoundingClientRect();

            renderingContext.resize(width, height);
        });

        resizeObserver.observe(container);

        return () => {
            resizeObserver.disconnect();
            renderingContext.dispose();

            renderingContextRef.current = null;
        };
    }, [containerRef, onSelectionChange]);

    useEffect(() => {
        renderingContextRef.current?.setReducedMotion(reducedMotion);
    }, [reducedMotion]);

    useEffect(() => {
        if (!solarWeather) {
            return;
        }

        renderingContextRef.current?.setSolarWeatherSnapshot(solarWeather);
    }, [solarWeather]);

    useEffect(() => {
        renderingContextRef.current?.setAnomalies(anomalies);
    }, [anomalies]);

    useEffect(() => {
        renderingContextRef.current?.setObservationVisualization(
            observationVisualization,
        );
    }, [observationVisualization]);

    const resetCamera = (): void => {
        renderingContextRef.current?.resetCamera();
    };

    const rotateCamera = (
        horizontalRadians: number,
        verticalRadians: number,
    ): void => {
        renderingContextRef.current?.rotateCamera(
            horizontalRadians,
            verticalRadians,
        );
    };

    const zoomCamera = (scale: number): void => {
        renderingContextRef.current?.zoomCamera(scale);
    };

    const selectAtViewportCenter = (): void => {
        renderingContextRef.current?.selectAtViewportCenter();
    };

    const clearCurrentSelection = (): void => {
        renderingContextRef.current?.clearCurrentSelection();
    };

    return {
        resetCamera,
        rotateCamera,
        zoomCamera,
        selectAtViewportCenter,
        clearCurrentSelection,
        setLayerVisible,
    };
}
