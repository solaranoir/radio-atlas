import {
  describe,
  expect,
  it,
} from "vitest";

import {
  TRANSITION_DURATIONS_SECONDS,
  TRANSITION_RATES_PER_SECOND,
  clampTransitionProgress,
  interpolateLinear,
} from "./transitionStandards";

describe("transition standards", () => {
  it("defines named transition durations", () => {
    expect(
      TRANSITION_DURATIONS_SECONDS,
    ).toEqual({
      quick: 0.2,
      standard: 0.4,
      deliberate: 0.6,
    });
  });

  it("defines shared transition rates", () => {
    expect(
      TRANSITION_RATES_PER_SECOND
        .opacity,
    ).toBe(1.5);
  });

  it("clamps transition progress between zero and one", () => {
    expect(
      clampTransitionProgress(
        -1,
        0.4,
      ),
    ).toBe(0);

    expect(
      clampTransitionProgress(
        0.2,
        0.4,
      ),
    ).toBe(0.5);

    expect(
      clampTransitionProgress(
        1,
        0.4,
      ),
    ).toBe(1);
  });

  it("completes immediately for zero-duration transitions", () => {
    expect(
      clampTransitionProgress(
        0,
        0,
      ),
    ).toBe(1);
  });

  it("interpolates linearly", () => {
    expect(
      interpolateLinear(
        0,
        10,
        0.5,
      ),
    ).toBe(5);
  });

  it("clamps interpolation progress", () => {
    expect(
      interpolateLinear(
        0,
        10,
        2,
      ),
    ).toBe(10);
  });
});
