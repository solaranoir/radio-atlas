import * as THREE from "three";

import type { SpotDensityRegion } from "../types/spotDensity";
import { geographicToGlobeCoordinates } from "../utilities/geographicCoordinates";
import { mapSpotDensityVisuals } from "../utilities/spotDensityVisuals";
import { EARTH_RADIUS } from "./createEarth";

const DENSITY_MARKER_RADIUS = 0.06;
const SURFACE_OFFSET = 0.012;

export type SpotDensityMarker = THREE.Mesh<
  THREE.CircleGeometry,
  THREE.MeshBasicMaterial
>;

export function createSpotDensityMarker(
  region: SpotDensityRegion,
): SpotDensityMarker {
  const geometry =
    new THREE.CircleGeometry(
      DENSITY_MARKER_RADIUS,
      32,
    );

  const visuals =
    mapSpotDensityVisuals(
      region.density,
    );

  const material =
    new THREE.MeshBasicMaterial({
      color: 0xffcc66,
      transparent: true,
      opacity: visuals.opacity,
      depthWrite: false,
      side: THREE.DoubleSide,
    });

  const marker =
    new THREE.Mesh(
      geometry,
      material,
    );

  const position =
    geographicToGlobeCoordinates(
      {
        latitude: region.latitude,
        longitude: region.longitude,
      },
      EARTH_RADIUS + SURFACE_OFFSET,
    );

  marker.position.set(
    position.x,
    position.y,
    position.z,
  );

  const outwardTarget =
    marker.position
      .clone()
      .multiplyScalar(2);

  marker.lookAt(outwardTarget);

  marker.userData.region = region;
  marker.userData.baseOpacity =
    visuals.opacity;
  marker.userData.pulseAmplitude =
    visuals.pulseAmplitude;
  marker.userData.pulseSpeed =
    visuals.pulseSpeed;
  marker.userData.elapsedTime = 0;

  return marker;
}
