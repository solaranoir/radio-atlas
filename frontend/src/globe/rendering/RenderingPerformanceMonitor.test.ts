import type * as THREE from "three";
import { describe, expect, it } from "vitest";

import {
  RenderingPerformanceMonitor,
} from "./RenderingPerformanceMonitor";

function createRendererStub(
  overrides?: Partial<{
    calls: number;
    triangles: number;
    geometries: number;
    textures: number;
  }>,
): THREE.WebGLRenderer {
  return {
    info: {
      render: {
        calls: overrides?.calls ?? 12,
        triangles: overrides?.triangles ?? 2400,
      },
      memory: {
        geometries: overrides?.geometries ?? 8,
        textures: overrides?.textures ?? 3,
      },
    },
  } as THREE.WebGLRenderer;
}

describe("RenderingPerformanceMonitor", () => {
  it("returns null before one second of samples has accumulated", () => {
    const renderer = createRendererStub();
    const monitor =
      new RenderingPerformanceMonitor(renderer);

    for (let frame = 0; frame < 59; frame += 1) {
      const snapshot = monitor.update(1 / 60);

      expect(snapshot).toBeNull();
    }
  });

  it("reports FPS after the sampling interval", () => {
    const renderer = createRendererStub();
    const monitor =
      new RenderingPerformanceMonitor(renderer);

    let snapshot = null;

    for (let frame = 0; frame < 60; frame += 1) {
      snapshot = monitor.update(1 / 60);
    }

    expect(snapshot).not.toBeNull();
    expect(snapshot?.fps).toBeCloseTo(60);
  });

  it("calculates frame time from FPS", () => {
    const renderer = createRendererStub();
    const monitor =
      new RenderingPerformanceMonitor(renderer);

    let snapshot = null;

    for (let frame = 0; frame < 60; frame += 1) {
      snapshot = monitor.update(1 / 60);
    }

    expect(snapshot).not.toBeNull();

    expect(
      snapshot?.frameTimeMs,
    ).toBeCloseTo(1000 / 60);
  });

  it("reports renderer draw calls, triangles, geometries, and textures", () => {
    const renderer = createRendererStub({
      calls: 17,
      triangles: 4200,
      geometries: 11,
      textures: 5,
    });

    const monitor =
      new RenderingPerformanceMonitor(renderer);

    let snapshot = null;

    for (let frame = 0; frame < 60; frame += 1) {
      snapshot = monitor.update(1 / 60);
    }

    expect(snapshot).not.toBeNull();
    expect(snapshot?.drawCalls).toBe(17);
    expect(snapshot?.triangles).toBe(4200);
    expect(snapshot?.geometries).toBe(11);
    expect(snapshot?.textures).toBe(5);
  });

  it("resets the sampling window after producing a snapshot", () => {
    const renderer = createRendererStub();
    const monitor =
      new RenderingPerformanceMonitor(renderer);

    let firstSnapshot = null;

    for (let frame = 0; frame < 60; frame += 1) {
      firstSnapshot = monitor.update(1 / 60);
    }

    expect(firstSnapshot).not.toBeNull();

    const nextFrameSnapshot =
      monitor.update(1 / 60);

    expect(nextFrameSnapshot).toBeNull();

    let secondSnapshot = null;

    for (let frame = 0; frame < 59; frame += 1) {
      secondSnapshot = monitor.update(1 / 60);
    }

    expect(secondSnapshot).not.toBeNull();
    expect(secondSnapshot?.fps).toBeCloseTo(60);
  });
});
