import {
  Object3D,
} from "three";
import {
  describe,
  expect,
  it,
} from "vitest";

import {
  isObjectVisible,
} from "./isObjectVisible";

describe("isObjectVisible", () => {
  it(
    "returns true when object and ancestors are visible",
    () => {
      const parent =
        new Object3D();
      const child =
        new Object3D();

      parent.add(child);

      expect(
        isObjectVisible(child),
      ).toBe(true);
    },
  );

  it(
    "returns false when object is hidden",
    () => {
      const object =
        new Object3D();

      object.visible = false;

      expect(
        isObjectVisible(object),
      ).toBe(false);
    },
  );

  it(
    "returns false when an ancestor is hidden",
    () => {
      const parent =
        new Object3D();
      const child =
        new Object3D();

      parent.add(child);
      parent.visible = false;

      expect(
        isObjectVisible(child),
      ).toBe(false);
    },
  );
});
