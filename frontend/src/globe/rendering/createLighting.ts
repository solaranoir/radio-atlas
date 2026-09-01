import * as THREE from "three";

export interface GlobeLighting {
  ambientLight: THREE.AmbientLight;
  directionalLight: THREE.DirectionalLight;
}

export function createLighting(): GlobeLighting {
  const ambientLight =
    new THREE.AmbientLight(
      0xffffff,
      1,
    );

  const directionalLight =
    new THREE.DirectionalLight(
      0xffffff,
      1.5,
    );

  return {
    ambientLight,
    directionalLight,
  };
}
