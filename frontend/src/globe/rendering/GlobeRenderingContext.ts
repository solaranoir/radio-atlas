import * as THREE from "three";

import { createAtmosphere } from "./createAtmosphere";
import { createCamera } from "./createCamera";
import { createEarth } from "./createEarth";
import { createLighting } from "./createLighting";
import { createRenderer } from "./createRenderer";
import { createStationMarker } from "./createStationMarker";


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

    const earth = createEarth();
    const atmosphere = createAtmosphere();

    this.scene.add(earth);
    this.scene.add(atmosphere);

    const stations = [
      {
        id: "las-vegas",
        callsign: "LAS-VEGAS",
        latitude: 36.1699,
        longitude: -115.1398,
      },
      {
        id: "new-york",
        callsign: "NEW-YORK",
        latitude: 40.7128,
        longitude: -74.006,
      },
      {
        id: "quito",
        callsign: "QUITO",
        latitude: -0.1807,
        longitude: -78.4678,
      },
    ];

    for (const station of stations) {
      this.scene.add(createStationMarker(station));
    }
  } 

  resize(width: number, height: number): void {
    if (width <= 0 || height <= 0) {
      return;
    }

    this.renderer.setSize(width, height);

    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
  }

  mount(container: HTMLElement): void {
    if (this.container !== null) {
      return;
    }

    this.container = container;
    this.container.appendChild(this.renderer.domElement);

    const { width, height } = container.getBoundingClientRect();

    this.resize(width, height);
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
