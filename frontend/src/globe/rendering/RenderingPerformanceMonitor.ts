import type * as THREE from "three";

export interface RenderingPerformanceSnapshot {
  fps: number;
  frameTimeMs: number;
  drawCalls: number;
  triangles: number;
  geometries: number;
  textures: number;
}

export class RenderingPerformanceMonitor {
  private frameCount = 0;
  private elapsedSeconds = 0;

  private readonly renderer: THREE.WebGLRenderer;

  constructor(renderer: THREE.WebGLRenderer) {
    this.renderer = renderer;
  }

  update(
    deltaSeconds: number,
  ): RenderingPerformanceSnapshot | null {
    this.frameCount += 1;
    this.elapsedSeconds += deltaSeconds;

    if (this.elapsedSeconds < 1) {
      return null;
    }

    const fps =
      this.frameCount /
      this.elapsedSeconds;

    const snapshot: RenderingPerformanceSnapshot = {
      fps,
      frameTimeMs:
        fps > 0 ? 1000 / fps : 0,
      drawCalls:
        this.renderer.info.render.calls,
      triangles:
        this.renderer.info.render.triangles,
      geometries:
        this.renderer.info.memory.geometries,
      textures:
        this.renderer.info.memory.textures,
    };

    this.frameCount = 0;
    this.elapsedSeconds = 0;

    return snapshot;
  }
}
