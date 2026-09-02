import * as THREE from "three";
import {
  describe,
  expect,
  it,
} from "vitest";

import {
  getHoverTooltip,
} from "./getHoverTooltip";

describe("getHoverTooltip", () => {
  it("creates station tooltip content", () => {
    const station =
      new THREE.Object3D();

    station.userData.station = {
      id: "las-vegas",
      callsign: "KK7QEA",
      latitude: 36.1699,
      longitude: -115.1398,
    };

    expect(
      getHoverTooltip(station),
    ).toEqual({
      title: "KK7QEA",
      details: [
        "36.17°, -115.14°",
      ],
    });
  });

  it("creates signal path tooltip content", () => {
    const path =
      new THREE.Object3D();

    path.userData.signalPath = {
      id: "vegas-new-york",
      source: {
        latitude: 36.1699,
        longitude: -115.1398,
      },
      target: {
        latitude: 40.7128,
        longitude: -74.006,
      },
      strength: 0.75,
    };

    expect(
      getHoverTooltip(path),
    ).toEqual({
      title: "Signal path",
      details: [
        "36.17°, -115.14° → 40.71°, -74.01°",
        "Strength: 0.75",
      ],
    });
  });

  it("returns null for unrelated objects", () => {
    expect(
      getHoverTooltip(
        new THREE.Object3D(),
      ),
    ).toBeNull();
  });
});
