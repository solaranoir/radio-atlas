import * as THREE from "three";
import {
  describe,
  expect,
  it,
} from "vitest";

import {
  findHoverTarget,
} from "./findHoverTarget";

function intersection(
  object: THREE.Object3D,
): THREE.Intersection {
  return {
    distance: 1,
    point: new THREE.Vector3(),
    object,
  };
}

describe("findHoverTarget", () => {
  it(
    "returns a station",
    () => {
      const station =
        new THREE.Mesh();

      station.userData.station = {
        id: "las-vegas",
      };

      expect(
        findHoverTarget([
          intersection(station),
        ]),
      ).toBe(station);
    },
  );

  it(
    "returns a signal path",
    () => {
      const path =
        new THREE.Line();

      path.userData.signalPath = {
        id: "vegas-new-york",
      };

      expect(
        findHoverTarget([
          intersection(path),
        ]),
      ).toBe(path);
    },
  );

  it(
    "prefers a station over a path",
    () => {
      const path =
        new THREE.Line();

      path.userData.signalPath = {
        id: "path",
      };

      const station =
        new THREE.Mesh();

      station.userData.station = {
        id: "station",
      };

      expect(
        findHoverTarget([
          intersection(path),
          intersection(station),
        ]),
      ).toBe(station);
    },
  );

  it(
    "returns null when nothing is selectable",
    () => {
      const earth =
        new THREE.Mesh();

      expect(
        findHoverTarget([
          intersection(earth),
        ]),
      ).toBeNull();
    },
  );
});
