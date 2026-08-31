import * as THREE from "three";

export interface GeographicCoordinates {
  latitude: number;
  longitude: number;
}

export interface GlobeCoordinates {
  x: number;
  y: number;
  z: number;
}

export function geographicToGlobeCoordinates(
  coordinates: GeographicCoordinates,
  radius = 1,
): GlobeCoordinates {
  const latitudeRadians = THREE.MathUtils.degToRad(
    coordinates.latitude,
  );

  const longitudeRadians = THREE.MathUtils.degToRad(
    coordinates.longitude,
  );

  const cosLatitude = Math.cos(latitudeRadians);

  return {
    x: radius * cosLatitude * Math.cos(longitudeRadians),
    y: radius * Math.sin(latitudeRadians),
    z: -radius * cosLatitude * Math.sin(longitudeRadians),
  };
}
