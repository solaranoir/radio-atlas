import {
  useRef,
} from "react";

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

  useGlobeRenderer(
    containerRef,
    solarWeather,
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
