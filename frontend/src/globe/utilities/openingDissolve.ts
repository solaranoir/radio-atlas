export type OpeningDissolveState =
  | "appearing"
  | "steady"
  | "disappearing";

export interface OpeningDissolveResult {
  opacity: number;
  complete: boolean;
}

const DISSOLVE_DURATION_SECONDS = 0.6;

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
    DISSOLVE_DURATION_SECONDS;

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
