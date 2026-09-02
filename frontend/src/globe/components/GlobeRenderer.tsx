import { useRef } from "react";

import { useAnomalies } from "../hooks/useAnomalies";
import { useGlobeRenderer } from "../hooks/useGlobeRenderer";
import { useSolarWeather } from "../hooks/useSolarWeather";
import { LayerControls } from "./LayerControls";

export function GlobeRenderer() {
    const containerRef = useRef<HTMLDivElement | null>(null);

    const { snapshot: solarWeather } = useSolarWeather();

    const { anomalies } = useAnomalies();

    const { resetCamera } = useGlobeRenderer(
        containerRef,
        solarWeather,
        anomalies,
    );

    const { setLayerVisible } = useGlobeRenderer(
        containerRef,
        solarWeather,
        anomalies,
    );

    return (
        <>
            <div className="globe-toolbar">
                <button
                    type="button"
                    onClick={resetCamera}
                    style={{
                        position: "absolute",
                        top: 16,
                        left: 16,
                        zIndex: 10,
                    }}
                >
                    Reset camera
                </button>

                <LayerControls onVisibilityChange={setLayerVisible} />
            </div>

            <div
                ref={containerRef}
                className="globe-container"
                style={{
                    width: "100%",
                    height: "100vh",
                    overflow: "hidden",
                }}
            />
        </>
    );
}
