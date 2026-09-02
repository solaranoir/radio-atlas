import type {
  GeographicCoordinates,
} from "./geographicCoordinates";

export function maidenheadToCoordinates(
  grid: string,
): GeographicCoordinates | null {
  const normalized =
    grid.trim().toUpperCase();

  if (
    normalized.length < 4 ||
    normalized.length > 6
  ) {
    return null;
  }

  const fieldLon =
    normalized.charCodeAt(0) -
    65;

  const fieldLat =
    normalized.charCodeAt(1) -
    65;

  const squareLon =
    Number(normalized[2]);

  const squareLat =
    Number(normalized[3]);

  if (
    fieldLon < 0 ||
    fieldLon > 17 ||
    fieldLat < 0 ||
    fieldLat > 17 ||
    Number.isNaN(squareLon) ||
    Number.isNaN(squareLat)
  ) {
    return null;
  }

  let longitude =
    -180 +
    fieldLon * 20 +
    squareLon * 2;

  let latitude =
    -90 +
    fieldLat * 10 +
    squareLat;

  let longitudeSize = 2;
  let latitudeSize = 1;

  if (normalized.length >= 6) {
    const subLon =
      normalized.charCodeAt(4) -
      65;

    const subLat =
      normalized.charCodeAt(5) -
      65;

    if (
      subLon < 0 ||
      subLon > 23 ||
      subLat < 0 ||
      subLat > 23
    ) {
      return null;
    }

    longitude +=
      subLon * (2 / 24);

    latitude +=
      subLat * (1 / 24);

    longitudeSize =
      2 / 24;

    latitudeSize =
      1 / 24;
  }

  return {
    longitude:
      longitude +
      longitudeSize / 2,

    latitude:
      latitude +
      latitudeSize / 2,
  };
}
