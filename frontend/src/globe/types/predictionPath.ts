import type {
  GeographicCoordinates,
} from "../utilities/geographicCoordinates";

export interface PredictionPath {
  id: string;

  source: GeographicCoordinates;
  target: GeographicCoordinates;

  /**
   * Prediction confidence expressed from
   * 0 (lowest) to 1 (highest).
   */
  confidence: number;
}
