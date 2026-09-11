import {
  describe,
  expect,
  it,
} from "vitest";
import * as THREE from "three";

import {
  PredictionPathLayer,
} from "./PredictionPathLayer";

const prediction = {
  id: "vegas-new-york",
  source: {
    latitude: 36.1699,
    longitude: -115.1398,
  },
  target: {
    latitude: 40.7128,
    longitude: -74.006,
  },
  confidence: 0.8,
};

describe("PredictionPathLayer", () => {
  it("renders prediction paths", () => {
    const layer =
      new PredictionPathLayer();

    layer.setPaths([
      prediction,
    ]);

    expect(
      layer.group.children,
    ).toHaveLength(1);

    layer.dispose();
  });

  it("uses dashed materials", () => {
    const layer =
      new PredictionPathLayer();

    layer.setPaths([
      prediction,
    ]);

    const line =
      layer.group.children[0];

    expect(
      line,
    ).toBeDefined();

    if (
      !line ||
      !("material" in line)
    ) {
      throw new Error(
        "Prediction line not created",
      );
    }

    expect(
      line.material,
    ).toMatchObject({
      isLineDashedMaterial: true,
    });

    layer.dispose();
  });

  it("replaces paths with the same id", () => {
    const layer =
      new PredictionPathLayer();

    layer.setPaths([
      prediction,
    ]);

    layer.setPaths([
      {
        ...prediction,
        confidence: 0.3,
      },
    ]);

    expect(
      layer.group.children,
    ).toHaveLength(1);

    layer.dispose();
  });

  it("removes paths no longer present", () => {
    const layer =
      new PredictionPathLayer();

    layer.setPaths([
      prediction,
    ]);

    layer.setPaths([]);

    expect(
      layer.group.children,
    ).toHaveLength(1);

    layer.update(0.6);

    expect(
      layer.group.children,
    ).toHaveLength(0);

    layer.dispose();
  });

  it("renders higher-confidence paths with greater opacity", () => {
    const layer =
      new PredictionPathLayer();

    layer.setPaths([
      {
        ...prediction,
        id: "low",
        confidence: 0.2,
      },
      {
        ...prediction,
        id: "high",
        confidence: 0.9,
      },
    ]);

    layer.update(0.6);

    const lowLine =
      layer.group.children[0] as THREE.Line<
        THREE.BufferGeometry,
        THREE.LineDashedMaterial
      >;

    const highLine =
      layer.group.children[1] as THREE.Line<
        THREE.BufferGeometry,
        THREE.LineDashedMaterial
      >;

    expect(
      highLine.material.opacity,
    ).toBeGreaterThan(
      lowLine.material.opacity,
    );

    layer.dispose();
  });

  it(
    "shows appearing paths immediately when reduced motion is enabled",
    () => {

      const reducedMotionLayer =
        new PredictionPathLayer();

      reducedMotionLayer.setPaths([
        prediction,
      ]);

      const reducedMotionLine =
        reducedMotionLayer.group.children[0] as THREE.Line<
          THREE.BufferGeometry,
          THREE.LineDashedMaterial
        >;

      reducedMotionLayer.update(
        0.016,
        true,
      );

      const reducedMotionOpacity =
        reducedMotionLine.material.opacity;

      const normalLayer =
        new PredictionPathLayer();

      normalLayer.setPaths([
        prediction,
      ]);

      const normalLine =
        normalLayer.group.children[0] as THREE.Line<
          THREE.BufferGeometry,
          THREE.LineDashedMaterial
        >;

      normalLayer.update(0.6);

      expect(
        reducedMotionOpacity,
      ).toBe(
        normalLine.material.opacity,
      );

      reducedMotionLayer.dispose();
      normalLayer.dispose();
    },
  );
});
