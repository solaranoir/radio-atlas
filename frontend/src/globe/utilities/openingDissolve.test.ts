import {
  describe,
  expect,
  it,
} from "vitest";

import {
  advanceOpeningDissolve,
} from "./openingDissolve";

describe("advanceOpeningDissolve", () => {
  it("dissolves an opening in toward its target opacity", () => {
    const result =
      advanceOpeningDissolve(
        0,
        0.8,
        "appearing",
        0.3,
      );

    expect(
      result.opacity,
    ).toBeCloseTo(0.5);

    expect(
      result.complete,
    ).toBe(false);
  });

  it("does not exceed the opening target opacity", () => {
    const result =
      advanceOpeningDissolve(
        0.7,
        0.8,
        "appearing",
        0.3,
      );

    expect(
      result.opacity,
    ).toBe(0.8);

    expect(
      result.complete,
    ).toBe(true);
  });

  it("dissolves a closing opening toward zero", () => {
    const result =
      advanceOpeningDissolve(
        0.8,
        0.8,
        "disappearing",
        0.3,
      );

    expect(
      result.opacity,
    ).toBeCloseTo(0.3);

    expect(
      result.complete,
    ).toBe(false);
  });

  it("completes once a closing opening reaches zero", () => {
    const result =
      advanceOpeningDissolve(
        0.2,
        0.8,
        "disappearing",
        0.3,
      );

    expect(
      result.opacity,
    ).toBe(0);

    expect(
      result.complete,
    ).toBe(true);
  });

  it("uses target opacity for steady openings", () => {
    const result =
      advanceOpeningDissolve(
        0.2,
        0.75,
        "steady",
        0.3,
      );

    expect(
      result.opacity,
    ).toBe(0.75);

    expect(
      result.complete,
    ).toBe(true);
  });

  it("ignores negative elapsed time", () => {
    const result =
      advanceOpeningDissolve(
        0.4,
        0.8,
        "appearing",
        -1,
      );

    expect(
      result.opacity,
    ).toBe(0.4);
  });
});
