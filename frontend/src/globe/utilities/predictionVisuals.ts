import {
  normalizePredictionConfidence,
} from "./predictionConfidence";

export interface PredictionVisuals {
  opacity: number;
  dashScale: number;
}

export function mapPredictionVisuals(
  confidence: number,
): PredictionVisuals {
  const normalized =
    normalizePredictionConfidence(
      confidence,
    );

  return {
    opacity:
      0.28 +
      normalized * 0.52,

    dashScale:
      0.6 +
      normalized * 0.4,
  };
}


