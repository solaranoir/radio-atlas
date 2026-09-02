import {
  describe,
  expect,
  it,
} from "vitest";

import {
  mapPredictionVisuals,
} from "./predictionVisuals";

describe("mapPredictionVisuals", () => {
  it("makes higher-confidence predictions more visible", () => {
    const low =
      mapPredictionVisuals(0.2);

    const high =
      mapPredictionVisuals(0.9);

    expect(
      high.opacity,
    ).toBeGreaterThan(
      low.opacity,
    );

    expect(
      high.dashScale,
    ).toBeGreaterThan(
      low.dashScale,
    );
  });

  it("clamps confidence before mapping visuals", () => {
    expect(
      mapPredictionVisuals(-1),
    ).toEqual(
      mapPredictionVisuals(0),
    );

    expect(
      mapPredictionVisuals(2),
    ).toEqual(
      mapPredictionVisuals(1),
    );
  });
});
