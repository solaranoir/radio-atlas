import * as THREE from "three";
import {
  describe,
  expect,
  it,
} from "vitest";

import type { SolarWeatherSnapshot } from "../types/solarWeather";
import { SolarWeatherLayer } from "./SolarWeatherLayer";

const snapshot: SolarWeatherSnapshot = {
  observedAt:
    "2026-09-01T12:00:00Z",

  aurora: [
    {
      latitude: 65,
      longitude: -150,
      intensity: 20,
    },
    {
      latitude: 67,
      longitude: -145,
      intensity: 80,
    },
  ],

  indicators: {
    kpIndex: 6,
    solarFlux: 145,
    sunspotNumber: 120,
    solarWindSpeed: 550,
  },
};

describe("SolarWeatherLayer", () => {
  it("creates the activity halo", () => {
    const layer =
      new SolarWeatherLayer();

    expect(
      layer.group.children,
    ).toHaveLength(2);

    layer.dispose();
  });

  it("renders auroral observations", () => {
    const layer =
      new SolarWeatherLayer();

    layer.setSnapshot(snapshot);

    const auroraGroup =
      layer.group.children.find(
        (child) =>
          child instanceof THREE.Group,
      );

    expect(
      auroraGroup,
    ).toBeDefined();

    expect(
      auroraGroup?.children,
    ).toHaveLength(2);

    layer.dispose();
  });

  it("stores the current snapshot", () => {
    const layer =
      new SolarWeatherLayer();

    layer.setSnapshot(snapshot);

    expect(
      layer.group.userData.snapshot,
    ).toEqual(snapshot);

    layer.dispose();
  });

  it("increases halo opacity for stronger Kp activity", () => {
    const layer =
      new SolarWeatherLayer();

    layer.setSnapshot({
      ...snapshot,
      indicators: {
        ...snapshot.indicators,
        kpIndex: 1,
      },
    });

    const halo =
      layer.group.children.find(
        (child) =>
          child instanceof THREE.Mesh,
      ) as THREE.Mesh<
        THREE.SphereGeometry,
        THREE.MeshBasicMaterial
      >;

    const weakOpacity =
      halo.material.opacity;

    layer.setSnapshot({
      ...snapshot,
      indicators: {
        ...snapshot.indicators,
        kpIndex: 8,
      },
    });

    expect(
      halo.material.opacity,
    ).toBeGreaterThan(
      weakOpacity,
    );

    layer.dispose();
  });

  it("replaces auroral observations on update", () => {
    const layer =
      new SolarWeatherLayer();

    layer.setSnapshot(snapshot);

    layer.setSnapshot({
      ...snapshot,
      aurora: [
        {
          latitude: 70,
          longitude: 20,
          intensity: 90,
        },
      ],
    });

    const auroraGroup =
      layer.group.children.find(
        (child) =>
          child instanceof THREE.Group,
      );

    expect(
      auroraGroup?.children,
    ).toHaveLength(1);

    layer.dispose();
  });
});
