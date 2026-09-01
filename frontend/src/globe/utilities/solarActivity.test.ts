import {
  describe,
  expect,
  it,
} from "vitest";

import { normalizeKpIndex } from "./solarActivity";

describe("normalizeKpIndex", () => {
  it("maps Kp zero to zero activity", () => {
    expect(
      normalizeKpIndex(0),
    ).toBe(0);
  });

  it("maps Kp nine to maximum activity", () => {
    expect(
      normalizeKpIndex(9),
    ).toBe(1);
  });

  it("normalizes intermediate Kp values", () => {
    expect(
      normalizeKpIndex(4.5),
    ).toBeCloseTo(0.5);
  });

  it("handles missing Kp data", () => {
    expect(
      normalizeKpIndex(null),
    ).toBe(0);
  });

  it("clamps values above the Kp range", () => {
    expect(
      normalizeKpIndex(12),
    ).toBe(1);
  });

  it("clamps negative values", () => {
    expect(
      normalizeKpIndex(-2),
    ).toBe(0);
  });
});
