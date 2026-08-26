import * as THREE from "three";

import { createCamera } from "./createCamera";
import { createLighting } from "./createLighting";
import { createRenderer } from "./createRenderer";

export class GlobeRenderingContext {
  private readonly scene: THREE.Scene;
  private readonly camera: THREE.PerspectiveCamera;
  private readonly renderer: THREE.WebGLRenderer;

  private animationFrameId: number | null = null;
  private container: HTMLElement | null = null;

  constructor() {
    this.scene = new THREE.Scene();
    this.camera = createCamera();
    this.renderer = createRenderer();

    const lights = createLighting();

    for (const light of lights) {
      this.scene.add(light);
    }
  } 

  mount(container: HTMLElement): void {
    if (this.container !== null) {
      return;
    }

    this.container = container;
    this.container.appendChild(this.renderer.domElement);
  }

  start(): void {
    if (this.animationFrameId !== null) {
      return;
    }

    this.animationFrameId = window.requestAnimationFrame(this.render);
  }

  stop(): void {
    if (this.animationFrameId === null) {
      return;
    }

    window.cancelAnimationFrame(this.animationFrameId);
    this.animationFrameId = null;
  }

  dispose(): void {
    this.stop();

    if (
      this.container !== null &&
      this.renderer.domElement.parentElement === this.container
    ) {
      this.container.removeChild(this.renderer.domElement);
    }

    this.renderer.dispose();
    this.container = null;
  }

  private render = (): void => {
    this.renderer.render(this.scene, this.camera);

    this.animationFrameId = window.requestAnimationFrame(this.render);
  };
}
