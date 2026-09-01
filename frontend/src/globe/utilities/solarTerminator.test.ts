import * as THREE from "three";
import {
  describe,
  expect,
  it,
} from "vitest";

import { generateSolarTerminator } from "./solarTerminator";

describe("generateSolarTerminator", () => {
  it("generates the requested number of segments", () => {
    const points =
      generateSolarTerminator(
        new THREE.Vector3(
          1,
          0,
          0,
        ),
        64,
      );

    expect(points).toHaveLength(
      65,
    );
  });

  it("keeps every point on the requested radius", () => {
    const points =
      generateSolarTerminator(
        new THREE.Vector3(
          1,
          0,
          0,
        ),
        64,
        2,
      );

    for (const point of points) {
      expect(
        point.length(),
      ).toBeCloseTo(2);
    }
  });

  it("keeps terminator points perpendicular to the Sun", () => {
    const sunDirection =
      new THREE.Vector3(
        1,
        0.5,
        -0.25,
      ).normalize();

    const points =
      generateSolarTerminator(
        sunDirection,
      );

    for (const point of points) {
      expect(
        point
          .clone()
          .normalize()
          .dot(sunDirection),
      ).toBeCloseTo(
        0,
        10,
      );
    }
  });

  it("closes the terminator loop", () => {
    const points =
      generateSolarTerminator(
        new THREE.Vector3(
          0,
          0,
          1,
        ),
      );

    expect(
      points[0]?.distanceTo(
        points[
          points.length - 1
        ]!,
      ),
    ).toBeCloseTo(0);
  });

  it("rejects insufficient segments", () => {
    expect(() =>
      generateSolarTerminator(
        new THREE.Vector3(
          1,
          0,
          0,
        ),
        2,
      ),
    ).toThrow(RangeError);
  });
});
