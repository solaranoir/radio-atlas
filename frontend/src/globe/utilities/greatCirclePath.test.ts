import { describe, expect, it } from "vitest";

import { generateGreatCirclePath } from "./greatCirclePath";

describe("generateGreatCirclePath", () => {
  it("includes the start and end points", () => {
    const points = generateGreatCirclePath(
      {
        latitude: 0,
        longitude: 0,
      },
      {
        latitude: 0,
        longitude: -90,
      },
      {
        segments: 4,
      },
    );

    expect(points).toHaveLength(5);

    expect(points[0]?.x).toBeCloseTo(1);
    expect(points[0]?.y).toBeCloseTo(0);
    expect(points[0]?.z).toBeCloseTo(0);

    expect(points[4]?.x).toBeCloseTo(0);
    expect(points[4]?.y).toBeCloseTo(0);
    expect(points[4]?.z).toBeCloseTo(1);
  });

  it("generates the requested number of segments", () => {
    const points = generateGreatCirclePath(
      {
        latitude: 0,
        longitude: 0,
      },
      {
        latitude: 45,
        longitude: -90,
      },
      {
        segments: 10,
      },
    );

    expect(points).toHaveLength(11);
  });

  it("keeps every point on the requested radius", () => {
    const radius = 2;

    const points = generateGreatCirclePath(
      {
        latitude: 36.1699,
        longitude: -115.1398,
      },
      {
        latitude: 40.7128,
        longitude: -74.006,
      },
      {
        segments: 20,
        radius,
      },
    );

    for (const point of points) {
      const magnitude = Math.sqrt(
        point.x ** 2 +
          point.y ** 2 +
          point.z ** 2,
      );

      expect(magnitude).toBeCloseTo(radius);
    }
  });

  it("follows the equator between equatorial coordinates", () => {
    const points = generateGreatCirclePath(
      {
        latitude: 0,
        longitude: 0,
      },
      {
        latitude: 0,
        longitude: -90,
      },
      {
        segments: 8,
      },
    );

    for (const point of points) {
      expect(point.y).toBeCloseTo(0);
    }
  });

  it("returns repeated points when start and end are identical", () => {
    const points = generateGreatCirclePath(
      {
        latitude: 36.1699,
        longitude: -115.1398,
      },
      {
        latitude: 36.1699,
        longitude: -115.1398,
      },
      {
        segments: 4,
      },
    );

    expect(points).toHaveLength(5);

    for (const point of points) {
      expect(point.x).toBeCloseTo(points[0]!.x);
      expect(point.y).toBeCloseTo(points[0]!.y);
      expect(point.z).toBeCloseTo(points[0]!.z);
    }
  });

  it("rejects segment counts below one", () => {
    expect(() =>
      generateGreatCirclePath(
        {
          latitude: 0,
          longitude: 0,
        },
        {
          latitude: 0,
          longitude: 90,
        },
        {
          segments: 0,
        },
      ),
    ).toThrow(RangeError);
  });

  it("generates a valid path between antipodal points", () => {
    const points = generateGreatCirclePath(
      {
        latitude: 0,
        longitude: 0,
      },
      {
        latitude: 0,
        longitude: 180,
       },
      {
        segments: 8,
      },
    );

    expect(points).toHaveLength(9);

    for (const point of points) {
      const magnitude = Math.sqrt(
        point.x ** 2 +
          point.y ** 2 +
          point.z ** 2,
      );

      expect(Number.isFinite(point.x)).toBe(true);
      expect(Number.isFinite(point.y)).toBe(true);
      expect(Number.isFinite(point.z)).toBe(true);
      expect(magnitude).toBeCloseTo(1);
    }

    const start = points[0]!;
    const end = points[points.length - 1]!;

    expect(start.x).toBeCloseTo(1);
    expect(start.y).toBeCloseTo(0);
    expect(start.z).toBeCloseTo(0);

    expect(end.x).toBeCloseTo(-1);
    expect(end.y).toBeCloseTo(0);
    expect(end.z).toBeCloseTo(0);
  });

  it("follows a curved great-circle route between distant stations", () => {
    const points = generateGreatCirclePath(
      {
        latitude: 40.7128,
        longitude: -74.006,
      },
      {
        latitude: 51.5074,
        longitude: -0.1278,
      },
      {
        segments: 10,
      },
    );

    expect(points).toHaveLength(11);

    const midpoint = points[5]!;

    const magnitude = Math.sqrt(
      midpoint.x ** 2 +
        midpoint.y ** 2 +
        midpoint.z ** 2,
    );
  
    expect(magnitude).toBeCloseTo(1);

    // Both endpoints are in the northern hemisphere,
    // so the midpoint must also lie north of the equator.
    expect(midpoint.y).toBeGreaterThan(0);
  });
});
