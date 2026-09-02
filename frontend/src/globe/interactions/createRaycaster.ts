import * as THREE from "three";

export interface PointerCoordinates {
  x: number;
  y: number;
}

export function createRaycaster(): THREE.Raycaster {
  const raycaster =
    new THREE.Raycaster();

  raycaster.params.Line.threshold =
    0.02;

  return raycaster;
}

export function pointerToNormalizedDeviceCoordinates(
  clientX: number,
  clientY: number,
  element: HTMLElement,
): PointerCoordinates {
  const bounds =
    element.getBoundingClientRect();

  return {
    x:
      ((clientX - bounds.left) /
        bounds.width) *
        2 -
      1,

    y:
      -(
        (clientY - bounds.top) /
          bounds.height
      ) *
        2 +
      1,
  };
}
