import type {
  AuroraObservation,
} from "../types/solarWeather";

export interface AuroraCoordinate {
  aurora: number;
  latitude: number;
  longitude: number;
}

const MINIMUM_AURORA_INTENSITY = 5;

export function mapAuroraCoordinates(
  coordinates: AuroraCoordinate[],
): AuroraObservation[] {
  return coordinates
    .filter(
      (coordinate) =>
        coordinate.aurora >=
        MINIMUM_AURORA_INTENSITY,
    )
    .map((coordinate) => ({
      latitude:
        coordinate.latitude,

      longitude:
        normalizeLongitude(
          coordinate.longitude,
        ),

      intensity:
        coordinate.aurora,
    }));
}

export function normalizeLongitude(
  longitude: number,
): number {
  return longitude > 180
    ? longitude - 360
    : longitude;
}
