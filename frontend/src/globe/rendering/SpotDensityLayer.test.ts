import * as THREE from "three";
import {
  describe,
  expect,
  it,
} from "vitest";

import type { SpotDensityRegion } from "../types/spotDensity";
import { SpotDensityLayer } from "./SpotDensityLayer";

const lowDensityRegion: SpotDensityRegion = {
  id: "low",
  latitude: 36,
  longitude: -115,
  count: 1,
  density: 0.25,
};

const highDensityRegion: SpotDensityRegion = {
  id: "high",
  latitude: 40,
  longitude: -74,
  count: 4,
  density: 1,
};

describe("SpotDensityLayer", () => {
  it("renders multiple density regions", () => {
    const layer =
      new SpotDensityLayer();

    layer.setRegions([
      lowDensityRegion,
      highDensityRegion,
    ]);

    expect(
      layer.group.children,
    ).toHaveLength(2);

    layer.dispose();
  });

  it("removes regions no longer present", () => {
    const layer =
      new SpotDensityLayer();

    layer.setRegions([
      lowDensityRegion,
      highDensityRegion,
    ]);

    layer.setRegions([
      highDensityRegion,
    ]);

    expect(
      layer.group.children,
    ).toHaveLength(1);

    layer.dispose();
  });

  it("pulses markers over time", () => {
    const layer =
      new SpotDensityLayer();

    layer.setRegions([
      highDensityRegion,
    ]);

    const marker =
      layer.group.children[0] as THREE.Mesh;

    const initialScale =
      marker.scale.x;

    layer.update(0.5);

    expect(
      marker.scale.x,
    ).toBeGreaterThan(
      initialScale,
    );

    layer.dispose();
  });

  it("updates visual intensity when density changes", () => {
    const layer =
      new SpotDensityLayer();

    layer.setRegions([
      lowDensityRegion,
    ]);

    const marker =
      layer.group.children[0] as THREE.Mesh<
        THREE.CircleGeometry,
        THREE.MeshBasicMaterial
      >;

    const initialBaseOpacity =
      marker.userData.baseOpacity as number;

    layer.setRegions([
      {
        ...lowDensityRegion,
        count: 10,
        density: 1,
      },
    ]);

    expect(
      marker.userData.baseOpacity,
    ).toBeGreaterThan(
      initialBaseOpacity,
    );

    layer.dispose();
  });

  it(
    "keeps markers static when reduced motion is enabled",
    () => {
      const layer =
        new SpotDensityLayer();

      layer.setRegions([
        highDensityRegion,
      ]);

      const marker =
        layer.group.children[0] as THREE.Mesh<
          THREE.CircleGeometry,
          THREE.MeshBasicMaterial
        >;

      layer.update(
        0.5,
        true,
      );

      const firstScale =
        marker.scale.x;

      const firstOpacity =
        marker.material.opacity;

      layer.update(
        0.5,
        true,
      );

      expect(
        marker.scale.x,
      ).toBe(firstScale);

      expect(
        marker.material.opacity,
      ).toBe(firstOpacity);

      layer.dispose();
    },
  );
});
