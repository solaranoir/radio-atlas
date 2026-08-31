import * as THREE from "three";

import type { Station } from "../types/station";
import { geographicToGlobeCoordinates } from "../utilities/geographicCoordinates";
import { normalizeCoordinates } from "../utilities/normalizeCoordinates";
import { EARTH_RADIUS } from "./createEarth";

const STATION_MARKER_RADIUS = 0.018;
const STATION_SURFACE_OFFSET = 0.01;

export function createStationMarker(
  station: Station,
): THREE.Mesh<
  THREE.SphereGeometry,
  THREE.MeshBasicMaterial
> {
  const geometry = new THREE.SphereGeometry(
    STATION_MARKER_RADIUS,
    16,
    16,
  );

  const material = new THREE.MeshBasicMaterial({
    color: 0xff4d4d,
  });

  const marker = new THREE.Mesh(
    geometry,
    material,
  );

  const coordinates = normalizeCoordinates({
    latitude: station.latitude,
    longitude: station.longitude,
  });

  const position = geographicToGlobeCoordinates(
    coordinates,
    EARTH_RADIUS + STATION_SURFACE_OFFSET,
  );

  marker.position.set(
    position.x,
    position.y,
    position.z,
  );

  marker.userData.station = station;

  return marker;
}
