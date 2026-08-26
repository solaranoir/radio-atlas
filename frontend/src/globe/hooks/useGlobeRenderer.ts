import { useEffect, type RefObject } from "react";

import { GlobeRenderingContext } from "../rendering/GlobeRenderingContext";

export function useGlobeRenderer(
  containerRef: RefObject<HTMLDivElement | null>,
): void {
  useEffect(() => {
    const container = containerRef.current;

    if (container === null) {
      return;
    }

    const renderingContext = new GlobeRenderingContext();

    renderingContext.mount(container);
    renderingContext.start();

    return () => {
      renderingContext.dispose();
    };
  }, [containerRef]);
}
