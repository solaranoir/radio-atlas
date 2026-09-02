import {
  OrbitControls,
} from "three/examples/jsm/controls/OrbitControls.js";
import type * as THREE from "three";

export function createNavigationControls(
  camera: THREE.PerspectiveCamera,
  domElement: HTMLElement,
): OrbitControls {
  const controls =
    new OrbitControls(
      camera,
      domElement,
    );

  controls.enableRotate = true;
  controls.enableZoom = true;
  controls.enablePan = true;

  controls.enableDamping = true;
  controls.dampingFactor = 0.08;

  controls.minDistance = 1.6;
  controls.maxDistance = 8;

  controls.target.set(
    0,
    0,
    0,
  );

  controls.update();

  controls.saveState();

  return controls;
}
