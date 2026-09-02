import {
  describe,
  expect,
  it,
} from "vitest";

import {
  createRaycaster,
  pointerToNormalizedDeviceCoordinates,
} from "./createRaycaster";

describe(
  "createRaycaster",
  () => {
    it("creates a raycaster", () => {
      const raycaster =
        createRaycaster();

      expect(raycaster).toBeDefined();
    });
  },
);

describe(
  "pointerToNormalizedDeviceCoordinates",
  () => {
    it(
      "maps the center of an element to zero",
      () => {
        const element = {
          getBoundingClientRect: () => ({
            left: 100,
            top: 50,
            width: 400,
            height: 200,
          }),
        } as HTMLElement;

        const coordinates =
          pointerToNormalizedDeviceCoordinates(
            300,
            150,
            element,
          );

        expect(coordinates.x).toBeCloseTo(0);
        expect(coordinates.y).toBeCloseTo(0);
      },
    );

    it(
      "maps the upper-left corner correctly",
      () => {
        const element = {
          getBoundingClientRect: () => ({
            left: 100,
            top: 50,
            width: 400,
            height: 200,
          }),
        } as HTMLElement;

        const coordinates =
          pointerToNormalizedDeviceCoordinates(
            100,
            50,
            element,
          );

        expect(coordinates.x).toBeCloseTo(-1);
        expect(coordinates.y).toBeCloseTo(1);
      },
    );
  },
);
