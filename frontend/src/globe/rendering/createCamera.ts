import * as THREE from "three";

export function createCamera(): THREE.PerspectiveCamera {
  const camera = new THREE.PerspectiveCamera(
    45,
    1,
    0.1,
    1000,
  );

  camera.position.set(0, 0, 3);

  return camera;
}
