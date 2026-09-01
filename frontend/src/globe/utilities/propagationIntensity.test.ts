import { describe, expect, it } from "vitest";

import {
  clampStrength,
  mapPropagationIntensity,
} from "./propagationIntensity";

describe("clampStrength", () => {
  it("preserves values inside the valid range", () => {
    expect(clampStrength(0.5)).toBe(0.5);
  });

  it("clamps values below zero", () => {
    expect(clampStrength(-1)).toBe(0);
  });

  it("clamps values above one", () => {
    expect(clampStrength(2)).toBe(1);
  });
});

describe("mapPropagationIntensity", () => {
  it("maps the weakest signal to minimum opacity", () => {
    expect(
      mapPropagationIntensity(0).opacity,
    ).toBeCloseTo(0.2);
  });

  it("maps the strongest signal to full opacity", () => {
    expect(
      mapPropagationIntensity(1).opacity,
    ).toBeCloseTo(1);
  });

  it("scales intermediate signal strength", () => {
    expect(
      mapPropagationIntensity(0.5).opacity,
    ).toBeCloseTo(0.6);
  });
});
