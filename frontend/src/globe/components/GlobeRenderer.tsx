import { useRef } from "react";

import { useGlobeRenderer } from "../hooks/useGlobeRenderer";

export function GlobeRenderer() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGlobeRenderer(containerRef);

  return (
    <div
      ref={containerRef}
      style={{
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
      }}
    />
  );
}
