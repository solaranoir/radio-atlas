import { describe, expect, it } from "vitest";

import { geographicToGlobeCoordinates } from "./geographicCoordinates";

const EPSILON = 1e-10;

describe("geographicToGlobeCoordinates", () => {
  it("places the prime meridian on the positive x axis", () => {
    const result = geographicToGlobeCoordinates({
      latitude: 0,
      longitude: 0,
    });

    expect(result.x).toBeCloseTo(1);
    expect(result.y).toBeCloseTo(0);
    expect(result.z).toBeCloseTo(0);
  });

  it("places 90 degrees west on the positive z axis", () => {
    const result = geographicToGlobeCoordinates({
      latitude: 0,
      longitude: -90,
    });

    expect(result.x).toBeCloseTo(0);
    expect(result.y).toBeCloseTo(0);
    expect(result.z).toBeCloseTo(1);
  });

  it("places 90 degrees east on the negative z axis", () => {
    const result = geographicToGlobeCoordinates({
      latitude: 0,
      longitude: 90,
    });

    expect(result.x).toBeCloseTo(0);
    expect(result.y).toBeCloseTo(0);
    expect(result.z).toBeCloseTo(-1);
  });

  it("places 180 degrees longitude on the negative x axis", () => {
    const result = geographicToGlobeCoordinates({
      latitude: 0,
      longitude: 180,
    });

    expect(result.x).toBeCloseTo(-1);
    expect(result.y).toBeCloseTo(0);
    expect(result.z).toBeCloseTo(0);
  });

  it("places the north pole on the positive y axis", () => {
    const result = geographicToGlobeCoordinates({
      latitude: 90,
      longitude: 0,
    });

    expect(Math.abs(result.x)).toBeLessThan(EPSILON);
    expect(result.y).toBeCloseTo(1);
    expect(Math.abs(result.z)).toBeLessThan(EPSILON);
  });

  it("places the south pole on the negative y axis", () => {
    const result = geographicToGlobeCoordinates({
      latitude: -90,
      longitude: 0,
    });

    expect(Math.abs(result.x)).toBeLessThan(EPSILON);
    expect(result.y).toBeCloseTo(-1);
    expect(Math.abs(result.z)).toBeLessThan(EPSILON);
  });

  it("converts a real-world coordinate to the expected globe position", () => {
    const result = geographicToGlobeCoordinates({
      latitude: 36.17,
      longitude: -115.14,
    });

    expect(result.x).toBeCloseTo(-0.34, 2);
    expect(result.y).toBeCloseTo(0.59, 2);
    expect(result.z).toBeCloseTo(0.73, 2);
  });

  it("scales coordinates to a custom radius", () => {
    const result = geographicToGlobeCoordinates(
      {
        latitude: 0,
        longitude: 0,
      },
      2,
    );

    expect(result.x).toBeCloseTo(2);
    expect(result.y).toBeCloseTo(0);
    expect(result.z).toBeCloseTo(0);
  });
});
