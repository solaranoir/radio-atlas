import {
  describe,
  expect,
  it,
} from "vitest";

import { normalizeAuroraIntensity } from "./auroraIntensity";

describe("normalizeAuroraIntensity", () => {
  it("maps zero activity to zero", () => {
    expect(
      normalizeAuroraIntensity(0),
    ).toBe(0);
  });

  it("maps maximum activity to one", () => {
    expect(
      normalizeAuroraIntensity(100),
    ).toBe(1);
  });

  it("normalizes intermediate activity", () => {
    expect(
      normalizeAuroraIntensity(50),
    ).toBeCloseTo(0.5);
  });

  it("clamps activity below zero", () => {
    expect(
      normalizeAuroraIntensity(-10),
    ).toBe(0);
  });

  it("clamps activity above maximum", () => {
    expect(
      normalizeAuroraIntensity(150),
    ).toBe(1);
  });
});
