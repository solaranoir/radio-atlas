import {
  describe,
  expect,
  it,
} from "vitest";

import {
  normalizePredictionConfidence,
} from "./predictionConfidence";

describe("normalizePredictionConfidence", () => {
  it("preserves values within the valid range", () => {
    expect(
      normalizePredictionConfidence(0.5),
    ).toBe(0.5);
  });

  it("preserves zero confidence", () => {
    expect(
      normalizePredictionConfidence(0),
    ).toBe(0);
  });

  it("preserves full confidence", () => {
    expect(
      normalizePredictionConfidence(1),
    ).toBe(1);
  });

  it("clamps values below zero", () => {
    expect(
      normalizePredictionConfidence(-0.5),
    ).toBe(0);
  });

  it("clamps values above one", () => {
    expect(
      normalizePredictionConfidence(1.5),
    ).toBe(1);
  });
});
