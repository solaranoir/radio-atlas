import {
  describe,
  expect,
  it,
} from "vitest";

import {
  resolveReducedMotion,
} from "./motionPreference";

describe(
  "resolveReducedMotion",
  () => {
    it(
      "uses the operating system setting when preference is system",
      () => {
        expect(
          resolveReducedMotion(
            "system",
            true,
          ),
        ).toBe(true);

        expect(
          resolveReducedMotion(
            "system",
            false,
          ),
        ).toBe(false);
      },
    );

    it(
      "forces reduced motion",
      () => {
        expect(
          resolveReducedMotion(
            "reduced",
            false,
          ),
        ).toBe(true);
      },
    );

    it(
      "forces full motion",
      () => {
        expect(
          resolveReducedMotion(
            "full",
            true,
          ),
        ).toBe(false);
      },
    );
  },
);
