import {
  normalizeAnomalySeverity,
} from "./anomalySeverity";

export interface AnomalyVisuals {
  opacity: number;
  scale: number;
  pulseSpeed: number;
}

export function mapAnomalyVisuals(
  severity: number,
): AnomalyVisuals {
  const normalized =
    normalizeAnomalySeverity(
      severity,
    );

  return {
    opacity:
      0.35 +
      normalized * 0.55,

    scale:
      0.8 +
      normalized * 0.7,

    pulseSpeed:
      0.8 +
      normalized * 1.7,
  };
}
