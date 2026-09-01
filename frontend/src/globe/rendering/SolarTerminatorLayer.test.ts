import * as THREE from "three";
import {
  describe,
  expect,
  it,
} from "vitest";

import { SolarTerminatorLayer } from "./SolarTerminatorLayer";

describe("SolarTerminatorLayer", () => {
  it("creates a terminator and night overlay", () => {
    const layer =
      new SolarTerminatorLayer(
        new Date(
          "2026-09-01T12:00:00Z",
        ),
      );

    expect(
      layer.group.children,
    ).toHaveLength(2);

    layer.dispose();
  });

  it("renders the terminator as a line", () => {
    const layer =
      new SolarTerminatorLayer(
        new Date(
          "2026-09-01T12:00:00Z",
        ),
      );

    const line =
      layer.group.children.find(
        (child) =>
          child instanceof THREE.Line,
      );

    expect(line).toBeDefined();

    layer.dispose();
  });

  it("renders a night hemisphere mesh", () => {
    const layer =
      new SolarTerminatorLayer(
        new Date(
          "2026-09-01T12:00:00Z",
        ),
      );

    const mesh =
      layer.group.children.find(
        (child) =>
          child instanceof THREE.Mesh,
      );

    expect(mesh).toBeDefined();

    layer.dispose();
  });

  it("updates when time changes", () => {
    const firstDate =
      new Date(
        "2026-09-01T12:00:00Z",
      );

    const secondDate =
      new Date(
        "2026-09-01T18:00:00Z",
      );

    const layer =
      new SolarTerminatorLayer(
        firstDate,
      );

    layer.update(secondDate);

    expect(
      layer.group.userData.date,
    ).toEqual(secondDate);

    layer.dispose();
  });
});
