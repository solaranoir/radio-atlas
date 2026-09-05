import {
  TRANSITION_DURATIONS_SECONDS,
} from "./transitionStandards";

export type OpeningDissolveState =
  | "appearing"
  | "steady"
  | "disappearing";

export interface OpeningDissolveResult {
  opacity: number;
  complete: boolean;
}

export function advanceOpeningDissolve(
  currentOpacity: number,
  targetOpacity: number,
  state: OpeningDissolveState,
  deltaSeconds: number,
): OpeningDissolveResult {
  const safeDelta =
    Math.max(0, deltaSeconds);

  const maxOpacityChange =
    safeDelta /
    TRANSITION_DURATIONS_SECONDS
      .deliberate;

  if (state === "appearing") {
    const opacity =
      Math.min(
        targetOpacity,
        currentOpacity +
          maxOpacityChange,
      );

    return {
      opacity,
      complete:
        opacity >= targetOpacity,
    };
  }

  if (state === "disappearing") {
    const opacity =
      Math.max(
        0,
        currentOpacity -
          maxOpacityChange,
      );

    return {
      opacity,
      complete: opacity <= 0,
    };
  }

  return {
    opacity: targetOpacity,
    complete: true,
  };
}
