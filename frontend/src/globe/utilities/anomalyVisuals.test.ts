import {
  describe,
  expect,
  it,
} from "vitest";

import {
  mapAnomalyVisuals,
} from "./anomalyVisuals";

describe("mapAnomalyVisuals", () => {
  it("makes severe anomalies more prominent", () => {
    const low =
      mapAnomalyVisuals(0.2);

    const high =
      mapAnomalyVisuals(0.9);

    expect(
      high.opacity,
    ).toBeGreaterThan(
      low.opacity,
    );

    expect(
      high.scale,
    ).toBeGreaterThan(
      low.scale,
    );

    expect(
      high.pulseSpeed,
    ).toBeGreaterThan(
      low.pulseSpeed,
    );
  });

  it("clamps severity before mapping visuals", () => {
    expect(
      mapAnomalyVisuals(-1),
    ).toEqual(
      mapAnomalyVisuals(0),
    );

    expect(
      mapAnomalyVisuals(2),
    ).toEqual(
      mapAnomalyVisuals(1),
    );
  });
});
