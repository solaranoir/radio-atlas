export interface AuroraVisuals {
  opacity: number;
  scale: number;
}

export interface SolarActivityVisuals {
  opacity: number;
}

export function mapAuroraVisuals(
  intensity: number,
): AuroraVisuals {
  const normalized =
    Math.max(
      0,
      Math.min(1, intensity),
    );

  return {
    opacity:
      0.08 +
      normalized * 0.42,

    scale:
      0.7 +
      normalized * 0.5,
  };
}

export function mapSolarActivityVisuals(
  activity: number,
): SolarActivityVisuals {
  const normalized =
    Math.max(
      0,
      Math.min(1, activity),
    );

  return {
    opacity:
      0.04 +
      normalized * 0.16,
  };
}
