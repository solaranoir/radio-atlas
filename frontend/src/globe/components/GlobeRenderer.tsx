import {
  useRef,
} from "react";

import {
  useAnomalies,
} from "../hooks/useAnomalies";
import { useGlobeRenderer } from "../hooks/useGlobeRenderer";
import { useSolarWeather } from "../hooks/useSolarWeather";

export function GlobeRenderer() {
  const containerRef =
    useRef<HTMLDivElement | null>(
      null,
    );

  const {
    snapshot: solarWeather,
  } = useSolarWeather();

  const {
    anomalies,
  } = useAnomalies();

  const {
    resetCamera,
  } = useGlobeRenderer(
    containerRef,
    solarWeather,
    anomalies,
  );

  return (
    <>
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

      <div
        ref={containerRef}
        style={{
          width: "100%",
          height: "100vh",
          overflow: "hidden",
        }}
      />
    </>
  );
}
