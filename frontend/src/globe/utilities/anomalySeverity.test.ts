import {
  describe,
  expect,
  it,
} from "vitest";

import {
  normalizeAnomalySeverity,
} from "./anomalySeverity";

describe("normalizeAnomalySeverity", () => {
  it("preserves values within range", () => {
    expect(
      normalizeAnomalySeverity(0.5),
    ).toBe(0.5);
  });

  it("clamps values below zero", () => {
    expect(
      normalizeAnomalySeverity(-0.25),
    ).toBe(0);
  });

  it("clamps values above one", () => {
    expect(
      normalizeAnomalySeverity(1.25),
    ).toBe(1);
  });
});
