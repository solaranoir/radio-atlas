import * as THREE from "three";

import type {
  GeographicCoordinates,
  GlobeCoordinates,
} from "./geographicCoordinates";
import { geographicToGlobeCoordinates } from "./geographicCoordinates";

export interface GreatCirclePathOptions {
  segments?: number;
  radius?: number;
}

const DEFAULT_SEGMENTS = 64;

export function generateGreatCirclePath(
  start: GeographicCoordinates,
  end: GeographicCoordinates,
  options: GreatCirclePathOptions = {},
): GlobeCoordinates[] {
  const segments = options.segments ?? DEFAULT_SEGMENTS;
  const radius = options.radius ?? 1;

  if (segments < 1) {
    throw new RangeError("segments must be at least 1");
  }

  const startVector = toUnitVector(start);
  const endVector = toUnitVector(end);

  const angle = startVector.angleTo(endVector);

  if (angle === 0) {
    const point = geographicToGlobeCoordinates(start, radius);

    return Array.from(
      { length: segments + 1 },
      () => ({ ...point }),
    );
  }

  const points: GlobeCoordinates[] = [];

  for (let index = 0; index <= segments; index += 1) {
    const fraction = index / segments;

    const vector = slerp(
      startVector,
      endVector,
      angle,
      fraction,
    ).multiplyScalar(radius);

    points.push({
      x: vector.x,
      y: vector.y,
      z: vector.z,
    });
  }

  return points;
}

function toUnitVector(
  coordinates: GeographicCoordinates,
): THREE.Vector3 {
  const point = geographicToGlobeCoordinates(coordinates);

  return new THREE.Vector3(
    point.x,
    point.y,
    point.z,
  ).normalize();
}

function slerp(
  start: THREE.Vector3,
  end: THREE.Vector3,
  angle: number,
  fraction: number,
): THREE.Vector3 {
  const sinAngle = Math.sin(angle);

  const startWeight =
    Math.sin((1 - fraction) * angle) / sinAngle;

  const endWeight =
    Math.sin(fraction * angle) / sinAngle;

  return new THREE.Vector3()
    .addScaledVector(start, startWeight)
    .addScaledVector(end, endWeight)
    .normalize();
}
