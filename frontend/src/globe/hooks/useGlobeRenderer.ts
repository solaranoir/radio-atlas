import { useEffect, type RefObject } from "react";

import { GlobeRenderingContext } from "../rendering/GlobeRenderingContext";

export function useGlobeRenderer(
  containerRef: RefObject<HTMLDivElement | null>,
): void {
  useEffect(() => {
    if (containerRef.current === null) {
      return;
    }

    const container: HTMLDivElement = containerRef.current;
    const renderingContext = new GlobeRenderingContext();

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
    };
  }, [containerRef]);
}
