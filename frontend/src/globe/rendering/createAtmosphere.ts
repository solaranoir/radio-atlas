import * as THREE from "three";

import { EARTH_RADIUS } from "./createEarth";

export function createAtmosphere(): THREE.Mesh<
  THREE.SphereGeometry,
  THREE.MeshBasicMaterial
> {
  const geometry = new THREE.SphereGeometry(
    EARTH_RADIUS * 1.015,
    64,
    32,
  );

  const material = new THREE.MeshBasicMaterial({
    color: 0x4da6ff,
    transparent: true,
    opacity: 0.08,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  return new THREE.Mesh(geometry, material);
}
