import type {
  Region,
} from "./globeFilters";

export interface GeographicPoint {
  latitude: number;
  longitude: number;
}

interface RegionBounds {
  minLatitude: number;
  maxLatitude: number;
  minLongitude: number;
  maxLongitude: number;
}

const REGION_BOUNDS: Record<
  Region,
  readonly RegionBounds[]
> = {
  "North America": [
    {
      minLatitude: 7,
      maxLatitude: 84,
      minLongitude: -170,
      maxLongitude: -50,
    },
  ],

  "South America": [
    {
      minLatitude: -56,
      maxLatitude: 13,
      minLongitude: -82,
      maxLongitude: -34,
    },
  ],

  Europe: [
    {
      minLatitude: 35,
      maxLatitude: 72,
      minLongitude: -25,
      maxLongitude: 45,
    },
  ],

  Africa: [
    {
      minLatitude: -35,
      maxLatitude: 37,
      minLongitude: -18,
      maxLongitude: 52,
    },
  ],

  Asia: [
    {
      minLatitude: -10,
      maxLatitude: 80,
      minLongitude: 45,
      maxLongitude: 180,
    },
  ],

  Oceania: [
    {
      minLatitude: -50,
      maxLatitude: 0,
      minLongitude: 110,
      maxLongitude: 180,
    },
    {
      minLatitude: -50,
      maxLatitude: 0,
      minLongitude: -180,
      maxLongitude: -130,
    },
  ],
};

export function getRegionForPoint(
  point: GeographicPoint,
): Region | null {
  const regions: readonly Region[] = [
    "North America",
    "South America",
    "Europe",
    "Africa",
    "Asia",
    "Oceania",
  ];

  for (const region of regions) {
    const matches =
      REGION_BOUNDS[
        region
      ].some(
        (bounds) =>
          point.latitude >=
            bounds.minLatitude &&
          point.latitude <=
            bounds.maxLatitude &&
          point.longitude >=
            bounds.minLongitude &&
          point.longitude <=
            bounds.maxLongitude,
      );

    if (matches) {
      return region;
    }
  }

  return null;
}
