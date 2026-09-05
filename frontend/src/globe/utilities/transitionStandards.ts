export const TRANSITION_DURATIONS_SECONDS = {
  quick: 0.2,
  standard: 0.4,
  deliberate: 0.6,
} as const;

export const TRANSITION_RATES_PER_SECOND = {
  opacity: 1.5,
} as const;

export function clampTransitionProgress(
  elapsedSeconds: number,
  durationSeconds: number,
): number {
  if (durationSeconds <= 0) {
    return 1;
  }

  return Math.min(
    1,
    Math.max(
      0,
      elapsedSeconds /
        durationSeconds,
    ),
  );
}

export function interpolateLinear(
  start: number,
  end: number,
  progress: number,
): number {
  const normalizedProgress =
    Math.min(
      1,
      Math.max(0, progress),
    );

  return (
    start +
    (
      end - start
    ) *
      normalizedProgress
  );
}
