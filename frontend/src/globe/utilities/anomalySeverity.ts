export function normalizeAnomalySeverity(
  severity: number,
): number {
  return Math.max(
    0,
    Math.min(
      1,
      severity,
    ),
  );
}
