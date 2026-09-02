import type {
  Object3D,
} from "three";

export function isObjectVisible(
  object: Object3D,
): boolean {
  let current:
    Object3D | null = object;

  while (current) {
    if (!current.visible) {
      return false;
    }

    current = current.parent;
  }

  return true;
}
