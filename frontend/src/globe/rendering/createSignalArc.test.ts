import { describe, expect, it } from "vitest";

import type { SignalPath } from "../types/signalPath";
import {
  createSignalArc,
  createSignalArcGeometry,
  updateSignalArc,
} from "./createSignalArc";
import { EARTH_RADIUS } from "./createEarth";

const signalPath: SignalPath = {
  id: "test-path",
  source: {
    latitude: 36.1699,
    longitude: -115.1398,
  },
  target: {
    latitude: 40.7128,
    longitude: -74.006,
  },
  strength: 0.5,
};

describe("createSignalArcGeometry", () => {
  it("creates one point for each segment boundary", () => {
    const geometry =
      createSignalArcGeometry(
        signalPath,
        10,
      );

    expect(
      geometry.getAttribute("position").count,
    ).toBe(11);

    geometry.dispose();
  });

  it("raises the midpoint above the globe surface", () => {
    const geometry =
      createSignalArcGeometry(
        signalPath,
        10,
        0.2,
      );

    const positions =
      geometry.getAttribute("position");

    const midpoint = 5;

    const x = positions.getX(midpoint);
    const y = positions.getY(midpoint);
    const z = positions.getZ(midpoint);

    const radius = Math.sqrt(
      x ** 2 + y ** 2 + z ** 2,
    );

    expect(radius).toBeGreaterThan(
      EARTH_RADIUS,
    );

    geometry.dispose();
  });
});

describe("createSignalArc", () => {
  it("associates the signal path with the rendered arc", () => {
    const arc = createSignalArc(signalPath);

    expect(
      arc.userData.signalPath,
    ).toEqual(signalPath);

    arc.geometry.dispose();
    arc.material.dispose();
  });
});

describe("updateSignalArc", () => {
  it("updates an existing arc with a new path", () => {
    const arc = createSignalArc(signalPath);

    const updatedPath: SignalPath = {
      ...signalPath,
      target: {
        latitude: 51.5074,
        longitude: -0.1278,
      },
    };

    updateSignalArc(
      arc,
      updatedPath,
    );

    expect(
      arc.userData.signalPath,
    ).toEqual(updatedPath);

    arc.geometry.dispose();
    arc.material.dispose();
  });

  it("maps propagation strength to arc opacity", () => {
    const weakArc = createSignalArc({
      ...signalPath,
      strength: 0,
    });

    const strongArc = createSignalArc({
      ...signalPath,
      strength: 1,
    });

    expect(
      weakArc.material.opacity,
    ).toBeLessThan(
      strongArc.material.opacity,
    );

    expect(
      strongArc.material.opacity,
    ).toBeCloseTo(1);

    weakArc.geometry.dispose();
    weakArc.material.dispose();

    strongArc.geometry.dispose();
    strongArc.material.dispose();
  });

  it("updates arc opacity when propagation strength changes", () => {
    const arc = createSignalArc({
      ...signalPath,
      strength: 0.1,
    });

    const initialOpacity =
      arc.material.opacity;

    updateSignalArc(
      arc,
      {
        ...signalPath,
        strength: 0.9,
      },
    );

    expect(
      arc.userData.targetOpacity,
    ).toBeGreaterThan(
      initialOpacity,
    );

    arc.geometry.dispose();
    arc.material.dispose();
  });
});
