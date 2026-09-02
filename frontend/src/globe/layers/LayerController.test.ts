import {
  describe,
  expect,
  it,
} from "vitest";

import type {
  GlobeLayerDefinition,
} from "./globeLayer";
import {
  LayerController,
} from "./LayerController";

const definitions:
  readonly GlobeLayerDefinition[] = [
    {
      id: "stations",
      label: "Stations",
      order: 10,
      defaultVisible: true,
    },
    {
      id: "anomalies",
      label: "Anomalies",
      order: 20,
      defaultVisible: false,
    },
  ];

describe("LayerController", () => {
  it(
    "uses default visibility",
    () => {
      const controller =
        new LayerController(
          definitions,
        );

      expect(
        controller.isVisible(
          "stations",
        ),
      ).toBe(true);

      expect(
        controller.isVisible(
          "anomalies",
        ),
      ).toBe(false);
    },
  );

  it(
    "enables a layer",
    () => {
      const controller =
        new LayerController(
          definitions,
        );

      controller.enable(
        "anomalies",
      );

      expect(
        controller.isVisible(
          "anomalies",
        ),
      ).toBe(true);
    },
  );

  it(
    "disables a layer",
    () => {
      const controller =
        new LayerController(
          definitions,
        );

      controller.disable(
        "stations",
      );

      expect(
        controller.isVisible(
          "stations",
        ),
      ).toBe(false);
    },
  );

  it(
    "toggles a layer",
    () => {
      const controller =
        new LayerController(
          definitions,
        );

      expect(
        controller.toggle(
          "stations",
        ),
      ).toBe(false);

      expect(
        controller.toggle(
          "stations",
        ),
      ).toBe(true);
    },
  );
});
