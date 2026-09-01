import {
  describe,
  expect,
  it,
} from "vitest";

import type { RadioObservation } from "../types/radioObservation";
import { calculateSpotDensity } from "./spotDensity";

describe("calculateSpotDensity", () => {
  it("returns no regions when there are no observations", () => {
    expect(
      calculateSpotDensity([]),
    ).toEqual([]);
  });

  it("creates a density region for an observation", () => {
    const observations: RadioObservation[] = [
      {
        id: "spot-one",
        latitude: 36.1699,
        longitude: -115.1398,
      },
    ];

    const regions =
      calculateSpotDensity(observations);

    expect(regions).toHaveLength(1);

    expect(regions[0]).toMatchObject({
      count: 1,
      density: 1,
    });
  });

  it("aggregates observations in the same geographic cell", () => {
    const observations: RadioObservation[] = [
      {
        id: "spot-one",
        latitude: 36.1,
        longitude: -115.1,
      },
      {
        id: "spot-two",
        latitude: 37.2,
        longitude: -116.4,
      },
    ];

    const regions =
      calculateSpotDensity(observations);

    expect(regions).toHaveLength(1);

    expect(regions[0]?.count).toBe(2);
  });

  it("creates separate regions for observations in different cells", () => {
    const observations: RadioObservation[] = [
      {
        id: "spot-one",
        latitude: 36,
        longitude: -115,
      },
      {
        id: "spot-two",
        latitude: 51,
        longitude: 0,
      },
    ];

    const regions =
      calculateSpotDensity(observations);

    expect(regions).toHaveLength(2);
  });

  it("normalizes density relative to the busiest region", () => {
    const observations: RadioObservation[] = [
      {
        id: "spot-one",
        latitude: 36.1,
        longitude: -115.1,
      },
      {
        id: "spot-two",
        latitude: 37.2,
        longitude: -116.4,
      },
      {
        id: "spot-three",
        latitude: 51.5,
        longitude: -0.1,
      },
    ];

    const regions =
      calculateSpotDensity(observations);

    const densities = regions
      .map((region) => region.density)
      .sort();

    expect(densities).toEqual([
      0.5,
      1,
    ]);
  });

  it("supports custom cell sizes", () => {
    const observations: RadioObservation[] = [
      {
        id: "spot-one",
        latitude: 10,
        longitude: 10,
      },
      {
        id: "spot-two",
        latitude: 16,
        longitude: 16,
      },
    ];

    const regions =
      calculateSpotDensity(
        observations,
        5,
      );

    expect(regions).toHaveLength(2);
  });

  it("rejects invalid cell sizes", () => {
    expect(() =>
      calculateSpotDensity([], 0),
    ).toThrow(RangeError);
  });
});
