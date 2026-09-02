import {
  describe,
  expect,
  it,
} from "vitest";

import {
  getGlobeLayerDefinition,
  globeLayerRegistry,
} from "./layerRegistry";

describe("globeLayerRegistry", () => {
  it(
    "contains unique layer ids",
    () => {
      const ids =
        globeLayerRegistry.map(
          (layer) => layer.id,
        );

      expect(
        new Set(ids).size,
      ).toBe(ids.length);
    },
  );

  it(
    "defines layers in ascending order",
    () => {
      const orders =
        globeLayerRegistry.map(
          (layer) => layer.order,
        );

      expect(orders).toEqual(
        [...orders].sort(
          (a, b) => a - b,
        ),
      );
    },
  );

  it(
    "defaults all current layers to visible",
    () => {
      expect(
        globeLayerRegistry.every(
          (layer) =>
            layer.defaultVisible,
        ),
      ).toBe(true);
    },
  );

  it(
    "returns a layer definition by id",
    () => {
      expect(
        getGlobeLayerDefinition(
          "signal-paths",
        ),
      ).toMatchObject({
        id: "signal-paths",
        label: "Signal Paths",
        order: 50,
      });
    },
  );
});
