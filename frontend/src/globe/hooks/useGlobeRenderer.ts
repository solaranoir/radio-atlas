import {
  useEffect,
  useRef,
  type RefObject,
} from "react";

import type { SolarWeatherSnapshot } from "../types/solarWeather";
import { GlobeRenderingContext } from "../rendering/GlobeRenderingContext";

export function useGlobeRenderer(
  containerRef: RefObject<HTMLDivElement | null>,
  solarWeather: SolarWeatherSnapshot | null,
): void {
  const renderingContextRef =
    useRef<GlobeRenderingContext | null>(
      null,
    );

  useEffect(() => {
    if (containerRef.current === null) {
      return;
    }

    const container =
      containerRef.current;

    const renderingContext =
      new GlobeRenderingContext();

    renderingContextRef.current =
      renderingContext;

    renderingContext.mount(
      container,
    );

    renderingContext.start();

    const resizeObserver =
      new ResizeObserver(() => {
        const {
          width,
          height,
        } =
          container.getBoundingClientRect();

        renderingContext.resize(
          width,
          height,
        );
      });

    resizeObserver.observe(
      container,
    );

    return () => {
      resizeObserver.disconnect();
      renderingContext.dispose();

      renderingContextRef.current =
        null;
    };
  }, [containerRef]);

  useEffect(() => {
    if (!solarWeather) {
      return;
    }

    renderingContextRef.current
      ?.setSolarWeatherSnapshot(
        solarWeather,
      );
  }, [solarWeather]);
}
