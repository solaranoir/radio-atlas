export function normalizeAuroraIntensity(
  intensity: number,
): number {
  return Math.max(
    0,
    Math.min(
      1,
      intensity / 100,
    ),
  );
}
