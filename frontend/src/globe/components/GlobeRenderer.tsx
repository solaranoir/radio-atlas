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

  useGlobeRenderer(
    containerRef,
    solarWeather,
    anomalies,
  );

  return (
    <div
      ref={containerRef}
      style={{
        width: "100%",
        height: "100vh",
        overflow: "hidden",
      }}
    />
  );
}
