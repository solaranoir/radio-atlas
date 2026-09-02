// @vitest-environment jsdom

import {
  describe,
  expect,
  it,
} from "vitest";
import * as THREE from "three";

import {
  createNavigationControls,
} from "./createNavigationControls";

describe(
  "createNavigationControls",
  () => {
    it(
      "enables globe navigation",
      () => {
        const camera =
          new THREE.PerspectiveCamera(
            45,
            1,
            0.1,
            1000,
          );

        camera.position.set(
          0,
          0,
          3,
        );

        const element =
          document.createElement(
            "div",
          );

        const controls =
          createNavigationControls(
            camera,
            element,
          );

        expect(
          controls.enableRotate,
        ).toBe(true);

        expect(
          controls.enableZoom,
        ).toBe(true);

        expect(
          controls.enablePan,
        ).toBe(true);

        expect(
          controls.enableDamping,
        ).toBe(true);

        expect(
          controls.minDistance,
        ).toBe(1.6);

        expect(
          controls.maxDistance,
        ).toBe(8);

        controls.dispose();
      },
    );
  },
);
