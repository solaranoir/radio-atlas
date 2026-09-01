export function normalizeKpIndex(
  kpIndex: number | null,
): number {
  if (kpIndex === null) {
    return 0;
  }

  return Math.max(
    0,
    Math.min(
      1,
      kpIndex / 9,
    ),
  );
}
