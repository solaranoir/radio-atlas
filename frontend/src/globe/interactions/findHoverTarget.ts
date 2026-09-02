import * as THREE from "three";

export type HoverTarget =
  | THREE.Object3D
  | null;

export function findHoverTarget(
  intersections:
    THREE.Intersection[],
): HoverTarget {
  const stationIntersection =
    intersections.find(
      ({ object }) =>
        object.userData.station,
    );

  if (stationIntersection) {
    return stationIntersection.object;
  }

  const signalPathIntersection =
    intersections.find(
      ({ object }) =>
        object.userData.signalPath,
    );

  return (
    signalPathIntersection?.object ??
    null
  );
}
