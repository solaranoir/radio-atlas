import {
  describe,
  expect,
  it,
} from "vitest";

import {
  isClickGesture,
} from "./isClickGesture";

describe("isClickGesture", () => {
  it(
    "accepts a stationary pointer",
    () => {
      expect(
        isClickGesture(
          { x: 100, y: 100 },
          { x: 100, y: 100 },
        ),
      ).toBe(true);
    },
  );

  it(
    "accepts movement within the threshold",
    () => {
      expect(
        isClickGesture(
          { x: 100, y: 100 },
          { x: 103, y: 104 },
        ),
      ).toBe(true);
    },
  );

  it(
    "rejects movement beyond the threshold",
    () => {
      expect(
        isClickGesture(
          { x: 100, y: 100 },
          { x: 106, y: 100 },
        ),
      ).toBe(false);
    },
  );
});
