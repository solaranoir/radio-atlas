export interface PropagationIntensity {
  opacity: number;
}

const MIN_OPACITY = 0.2;
const MAX_OPACITY = 1;

export function clampStrength(
  strength: number,
): number {
  return Math.max(0, Math.min(1, strength));
}

export function mapPropagationIntensity(
  strength: number,
): PropagationIntensity {
  const normalizedStrength =
    clampStrength(strength);

  const opacity =
    MIN_OPACITY +
    normalizedStrength *
      (MAX_OPACITY - MIN_OPACITY);

  return {
    opacity,
  };
}
