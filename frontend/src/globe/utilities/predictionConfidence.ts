export function normalizePredictionConfidence(
  confidence: number,
): number {
  return Math.max(
    0,
    Math.min(
      1,
      confidence,
    ),
  );
}
