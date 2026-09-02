import type {
  GeographicCoordinates,
} from "../utilities/geographicCoordinates";

export interface Anomaly {
  id: string;
  location: GeographicCoordinates;
  severity: number;
}
