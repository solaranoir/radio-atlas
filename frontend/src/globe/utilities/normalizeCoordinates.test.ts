import { describe, expect, it } from "vitest";

import { normalizeCoordinates } from "./normalizeCoordinates";

describe("normalizeCoordinates", () => {
  it("leaves valid coordinates unchanged", () => {
    expect(
      normalizeCoordinates({
        latitude: 36.17,
        longitude: -115.14,
      }),
    ).toEqual({
      latitude: 36.17,
      longitude: -115.14,
    });
  });

  it("clamps latitude above 90 degrees", () => {
    expect(
      normalizeCoordinates({
        latitude: 100,
        longitude: 0,
      }).latitude,
    ).toBe(90);
  });

  it("clamps latitude below -90 degrees", () => {
    expect(
      normalizeCoordinates({
        latitude: -100,
        longitude: 0,
      }).latitude,
    ).toBe(-90);
  });

  it("wraps longitude greater than 180 degrees", () => {
    expect(
      normalizeCoordinates({
        latitude: 0,
        longitude: 190,
      }).longitude,
    ).toBe(-170);
  });

  it("wraps longitude less than -180 degrees", () => {
    expect(
      normalizeCoordinates({
        latitude: 0,
        longitude: -190,
      }).longitude,
    ).toBe(170);
  });

  it("wraps a full rotation to zero", () => {
    expect(
      normalizeCoordinates({
        latitude: 0,
        longitude: 360,
      }).longitude,
    ).toBe(0);
  });

  it("preserves positive 180 degrees longitude", () => {
    expect(
      normalizeCoordinates({
        latitude: 0,
        longitude: 180,
      }).longitude,
    ).toBe(180);
  });

  it("preserves negative 180 degrees longitude", () => {
    expect(
      normalizeCoordinates({
        latitude: 0,
        longitude: -180,
      }).longitude,
    ).toBe(-180);
  });
});
