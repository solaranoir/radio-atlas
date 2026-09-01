import {
  describe,
  expect,
  it,
} from "vitest";

import { mapSpotDensityVisuals } from "./spotDensityVisuals";

describe("mapSpotDensityVisuals", () => {
  it("maps low density to minimum visual intensity", () => {
    const visuals =
      mapSpotDensityVisuals(0);

    expect(visuals.opacity).toBeCloseTo(
      0.25,
    );

    expect(
      visuals.pulseAmplitude,
    ).toBeCloseTo(0.05);

    expect(
      visuals.pulseSpeed,
    ).toBeCloseTo(1);
  });

  it("maps high density to maximum visual intensity", () => {
    const visuals =
      mapSpotDensityVisuals(1);

    expect(visuals.opacity).toBeCloseTo(
      0.8,
    );

    expect(
      visuals.pulseAmplitude,
    ).toBeCloseTo(0.3);

    expect(
      visuals.pulseSpeed,
    ).toBeCloseTo(3);
  });

  it("scales intermediate density values", () => {
    const visuals =
      mapSpotDensityVisuals(0.5);

    expect(visuals.opacity).toBeCloseTo(
      0.525,
    );

    expect(
      visuals.pulseAmplitude,
    ).toBeCloseTo(0.175);

    expect(
      visuals.pulseSpeed,
    ).toBeCloseTo(2);
  });

  it("clamps density below zero", () => {
    expect(
      mapSpotDensityVisuals(-1),
    ).toEqual(
      mapSpotDensityVisuals(0),
    );
  });

  it("clamps density above one", () => {
    expect(
      mapSpotDensityVisuals(2),
    ).toEqual(
      mapSpotDensityVisuals(1),
    );
  });
});
