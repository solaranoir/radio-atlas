import type { GeographicCoordinates } from "./geographicCoordinates";

export function normalizeCoordinates(
  coordinates: GeographicCoordinates,
): GeographicCoordinates {
  const latitude = Math.max(
    -90,
    Math.min(90, coordinates.latitude),
  );

  const longitude = normalizeLongitude(coordinates.longitude);

  return {
    latitude,
    longitude,
  };
}

function normalizeLongitude(longitude: number): number {
  if (longitude >= -180 && longitude <= 180) {
    return longitude;
  }

  return ((longitude + 180) % 360 + 360) % 360 - 180;
}
