import * as THREE from "three";

import type { SignalPath } from "../types/signalPath";
import { generateGreatCirclePath } from "../utilities/greatCirclePath";
import { mapPropagationIntensity } from "../utilities/propagationIntensity";
import { EARTH_RADIUS } from "./createEarth";

const DEFAULT_SEGMENTS = 64;
const DEFAULT_ARC_HEIGHT = 0.15;
const SURFACE_OFFSET = 0.005;

export function createSignalArc(
  signalPath: SignalPath,
): THREE.Line<
  THREE.BufferGeometry,
  THREE.LineBasicMaterial
> {
  const geometry = createSignalArcGeometry(signalPath);

  const intensity =
    mapPropagationIntensity(
      signalPath.strength,
    );

  const material = new THREE.LineBasicMaterial({
    color: 0x66ccff,
    transparent: true,
    opacity: intensity.opacity,
  });

  const arc = new THREE.Line(
    geometry,
    material,
  );

  arc.userData.signalPath = signalPath;
  arc.userData.targetOpacity =
  intensity.opacity;

  return arc;
}

export function createSignalArcGeometry(
  signalPath: SignalPath,
  segments = DEFAULT_SEGMENTS,
  arcHeight = DEFAULT_ARC_HEIGHT,
): THREE.BufferGeometry {
  const path = generateGreatCirclePath(
    signalPath.source,
    signalPath.target,
    {
      segments,
      radius: EARTH_RADIUS,
    },
  );

  const points = path.map((point, index) => {
    const fraction = index / (path.length - 1);

    const elevation =
      SURFACE_OFFSET +
      arcHeight * Math.sin(Math.PI * fraction);

    const radius =
      EARTH_RADIUS + elevation;

    return new THREE.Vector3(
      point.x,
      point.y,
      point.z,
    )
      .normalize()
      .multiplyScalar(radius);
  });

  return new THREE.BufferGeometry().setFromPoints(
    points,
  );
}

export function updateSignalArc(
  arc: THREE.Line<
    THREE.BufferGeometry,
    THREE.LineBasicMaterial
  >,
  signalPath: SignalPath,
): void {
  const previousGeometry = arc.geometry;

  arc.geometry =
    createSignalArcGeometry(signalPath);

  const intensity =
    mapPropagationIntensity(
      signalPath.strength,
    );

  arc.userData.signalPath =
    signalPath;

  arc.userData.targetOpacity =
    intensity.opacity;

  previousGeometry.dispose();
}
