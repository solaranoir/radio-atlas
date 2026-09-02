import { useCallback, useEffect, useRef, type RefObject } from "react";

import type { Anomaly } from "../types/anomaly";
import type { GlobeLayerId } from "../layers/globeLayer";
import type { SolarWeatherSnapshot } from "../types/solarWeather";
import { GlobeRenderingContext } from "../rendering/GlobeRenderingContext";

export function useGlobeRenderer(
    containerRef: RefObject<HTMLDivElement | null>,
    solarWeather: SolarWeatherSnapshot | null,
    anomalies: Anomaly[],
): {
    resetCamera: () => void;
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
        if (containerRef.current === null) {
            return;
        }

        const container = containerRef.current;

        const renderingContext = new GlobeRenderingContext();

        renderingContextRef.current = renderingContext;

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
    }, [containerRef]);

    useEffect(() => {
        if (!solarWeather) {
            return;
        }

        renderingContextRef.current?.setSolarWeatherSnapshot(solarWeather);
    }, [solarWeather]);

    useEffect(() => {
        renderingContextRef.current?.setAnomalies(anomalies);
    }, [anomalies]);

    const resetCamera = (): void => {
        renderingContextRef.current?.resetCamera();
    };

    return {
        resetCamera,
        setLayerVisible,
    };
}
