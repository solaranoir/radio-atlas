import * as THREE from "three";

export const EARTH_RADIUS = 1;

export function createEarth(): THREE.Mesh<
  THREE.SphereGeometry,
  THREE.MeshStandardMaterial
> {
  const geometry = new THREE.SphereGeometry(
    EARTH_RADIUS,
    64,
    32,
  );

  const texture = new THREE.TextureLoader().load(
    "/textures/earth/earth-day.jpg",
  );

  texture.colorSpace = THREE.SRGBColorSpace;

  const material = new THREE.MeshStandardMaterial({
    map: texture,
    roughness: 0.8,
    metalness: 0,
  });

  return new THREE.Mesh(geometry, material);
}
