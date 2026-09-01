import * as THREE from "three";

import type { GeographicCoordinates } from "./geographicCoordinates";

export interface SolarPosition {
  subsolarPoint: GeographicCoordinates;
  direction: THREE.Vector3;
}

export function calculateSolarPosition(
  date: Date,
): SolarPosition {
  const dayOfYear =
    getDayOfYear(date);

  const utcHours =
    date.getUTCHours() +
    date.getUTCMinutes() / 60 +
    date.getUTCSeconds() / 3600;

  const fractionalYear =
    (
      2 *
      Math.PI /
      365
    ) *
    (
      dayOfYear -
      1 +
      (
        utcHours -
        12
      ) /
      24
    );

  const equationOfTime =
    229.18 *
    (
      0.000075 +
      0.001868 *
        Math.cos(fractionalYear) -
      0.032077 *
        Math.sin(fractionalYear) -
      0.014615 *
        Math.cos(
          2 * fractionalYear,
        ) -
      0.040849 *
        Math.sin(
          2 * fractionalYear,
        )
    );

  const declinationRadians =
    0.006918 -
    0.399912 *
      Math.cos(fractionalYear) +
    0.070257 *
      Math.sin(fractionalYear) -
    0.006758 *
      Math.cos(
        2 * fractionalYear,
      ) +
    0.000907 *
      Math.sin(
        2 * fractionalYear,
      ) -
    0.002697 *
      Math.cos(
        3 * fractionalYear,
      ) +
    0.00148 *
      Math.sin(
        3 * fractionalYear,
      );

  const latitude =
    THREE.MathUtils.radToDeg(
      declinationRadians,
    );

  const utcMinutes =
    utcHours * 60;

  const longitude =
    normalizeLongitude(
      180 -
        (
          utcMinutes +
          equationOfTime
        ) /
          4,
    );

  const direction =
    geographicDirection({
      latitude,
      longitude,
    });

  return {
    subsolarPoint: {
      latitude,
      longitude,
    },
    direction,
  };
}

function geographicDirection(
  coordinates: GeographicCoordinates,
): THREE.Vector3 {
  const latitude =
    THREE.MathUtils.degToRad(
      coordinates.latitude,
    );

  const longitude =
    THREE.MathUtils.degToRad(
      coordinates.longitude,
    );

  const cosLatitude =
    Math.cos(latitude);

  return new THREE.Vector3(
    cosLatitude *
      Math.cos(longitude),
    Math.sin(latitude),
    -cosLatitude *
      Math.sin(longitude),
  ).normalize();
}

function normalizeLongitude(
  longitude: number,
): number {
  return (
    (
      (
        longitude +
        180
      ) %
        360 +
      360
    ) %
      360
  ) - 180;
}

function getDayOfYear(
  date: Date,
): number {
  const startOfYear =
    Date.UTC(
      date.getUTCFullYear(),
      0,
      0,
    );

  const current =
    Date.UTC(
      date.getUTCFullYear(),
      date.getUTCMonth(),
      date.getUTCDate(),
    );

  return Math.floor(
    (
      current -
      startOfYear
    ) /
      86_400_000,
  );
}
