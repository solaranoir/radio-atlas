import type { GeographicCoordinates } from "../utilities/geographicCoordinates";

export interface SignalPath {
  id: string;
  source: GeographicCoordinates;
  target: GeographicCoordinates;
}
