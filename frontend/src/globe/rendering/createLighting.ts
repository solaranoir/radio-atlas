import * as THREE from "three";

export function createLighting(): THREE.Light[] {
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);

  const directionalLight = new THREE.DirectionalLight(
    0xffffff,
    1.5,
  );

  directionalLight.position.set(5, 3, 5);

  return [ambientLight, directionalLight];
}
