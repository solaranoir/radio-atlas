import type {
  RadioObservation,
} from "../../api/observations";
import type {
  Anomaly,
} from "../types/anomaly";
import {
  maidenheadToCoordinates,
} from "./maidenhead";

const EARTH_RADIUS_KM = 6371;
const MAX_DISTANCE_KM = 12000;
const MIN_ANOMALY_SCORE = 0.65;

export function detectAnomalies(
  observations: RadioObservation[],
): Anomaly[] {
  return observations
    .map(toAnomaly)
    .filter(
      (
        anomaly,
      ): anomaly is Anomaly =>
        anomaly !== null,
    );
}

function toAnomaly(
  observation: RadioObservation,
): Anomaly | null {
  if (
    !observation.sender_grid ||
    !observation.receiver_grid
  ) {
    return null;
  }

  const source =
    maidenheadToCoordinates(
      observation.sender_grid,
    );

  const target =
    maidenheadToCoordinates(
      observation.receiver_grid,
    );

  if (
    !source ||
    !target
  ) {
    return null;
  }

  const distanceKm =
    calculateDistanceKm(
      source.latitude,
      source.longitude,
      target.latitude,
      target.longitude,
    );

  const distanceScore =
    Math.min(
      1,
      distanceKm /
        MAX_DISTANCE_KM,
    );

  const snrScore =
    normalizeSnr(
      observation.snr_db,
    );

  const severity =
    distanceScore * 0.65 +
    snrScore * 0.35;

  if (
    severity <
    MIN_ANOMALY_SCORE
  ) {
    return null;
  }

  return {
    id:
      `observation-${observation.id}`,

    location:
      target,

    severity,
  };
}

function normalizeSnr(
  snrDb: number | null,
): number {
  if (snrDb === null) {
    return 0;
  }

  return Math.max(
    0,
    Math.min(
      1,
      (snrDb + 30) / 40,
    ),
  );
}

function calculateDistanceKm(
  latitudeA: number,
  longitudeA: number,
  latitudeB: number,
  longitudeB: number,
): number {
  const toRadians =
    (degrees: number) =>
      degrees *
      Math.PI /
      180;

  const deltaLatitude =
    toRadians(
      latitudeB -
        latitudeA,
    );

  const deltaLongitude =
    toRadians(
      longitudeB -
        longitudeA,
    );

  const latitudeARadians =
    toRadians(latitudeA);

  const latitudeBRadians =
    toRadians(latitudeB);

  const haversine =
    Math.sin(
      deltaLatitude / 2,
    ) ** 2 +
    Math.cos(
      latitudeARadians,
    ) *
      Math.cos(
        latitudeBRadians,
      ) *
      Math.sin(
        deltaLongitude / 2,
      ) ** 2;

  return (
    EARTH_RADIUS_KM *
    2 *
    Math.atan2(
      Math.sqrt(haversine),
      Math.sqrt(
        1 - haversine,
      ),
    )
  );
}
