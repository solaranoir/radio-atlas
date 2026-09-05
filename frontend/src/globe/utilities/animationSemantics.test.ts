import {
  describe,
  expect,
  it,
} from "vitest";

import {
  ANIMATION_SEMANTICS,
} from "./animationSemantics";

describe("ANIMATION_SEMANTICS", () => {
  it("defines the five globe animation meanings", () => {
    expect(
      ANIMATION_SEMANTICS.map(
        ({ semantic }) => semantic,
      ),
    ).toEqual([
      "density-pulse",
      "strength-brightness",
      "opening-dissolve",
      "terminator-sweep",
      "anomaly-flare",
    ]);
  });

  it("assigns information to every animation", () => {
    for (
      const definition
      of ANIMATION_SEMANTICS
    ) {
      expect(
        definition.communicates.length,
      ).toBeGreaterThan(0);
    }
  });
});
