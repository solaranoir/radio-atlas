import * as THREE from "three";

import { createAtmosphere } from "./createAtmosphere";
import { createCamera } from "./createCamera";
import { createEarth } from "./createEarth";
import { createLighting } from "./createLighting";
import { createRenderer } from "./createRenderer";
import { createStationMarker } from "./createStationMarker";
import { SignalArcCollection } from "./SignalArcCollection";
import { SpotDensityLayer } from "./SpotDensityLayer";
import { calculateSpotDensity } from "../utilities/spotDensity";

export class GlobeRenderingContext {
  private readonly scene: THREE.Scene;
  private readonly camera: THREE.PerspectiveCamera;
  private readonly renderer: THREE.WebGLRenderer;
  private readonly clock = new THREE.Clock();
  private readonly signalArcs =
    new SignalArcCollection();
  private readonly spotDensity =
    new SpotDensityLayer();

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
    this.scene.add(this.signalArcs.group);
    this.scene.add(this.spotDensity.group);

    this.signalArcs.setPaths([
      {
        id: "las-vegas-new-york",
        source: {
          latitude: 36.1699,
          longitude: -115.1398,
        },
        target: {
          latitude: 40.7128,
          longitude: -74.006,
        },
        strength: 0.2,
      },
      {
        id: "new-york-london",
        source: {
          latitude: 40.7128,
          longitude: -74.006,
        },
        target: {
          latitude: 51.5074,
          longitude: -0.1278,
        },
       strength: 1,
      },
      {
        id: "quito-las-vegas",
        source: {
          latitude: -0.1807,
          longitude: -78.4678,
        },
        target: {
          latitude: 36.1699,
          longitude: -115.1398,
        },
       strength: 0.6,
      },
    ]);

  const densityObservations = [
    {
      id: "vegas-1",
      latitude: 36.1699,
      longitude: -115.1398,
    },
    {
      id: "vegas-2",
      latitude: 36.2,
      longitude: -115.2,
    },
    {
      id: "vegas-3",
      latitude: 37.1,
      longitude: -116.1,
    },
    {
      id: "new-york-1",
      latitude: 40.7128,
      longitude: -74.006,
    },
    {
      id: "london-1",
      latitude: 51.5074,
      longitude: -0.1278,
    },
    {
      id: "london-2",
      latitude: 52.1,
      longitude: -1.2,
    },
  ];

  this.spotDensity.setRegions(
    calculateSpotDensity(
      densityObservations,
    ),
  );

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
      this.clock.start();
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
    this.clock.stop();
    this.stop();

    if (
      this.container !== null &&
      this.renderer.domElement.parentElement === this.container
    ) {
      this.container.removeChild(this.renderer.domElement);
    }
    this.signalArcs.dispose();
    this.spotDensity.dispose();
    this.renderer.dispose();
    this.container = null;
  }

  private render = (): void => {
    const deltaSeconds = this.clock.getDelta();

    this.signalArcs.update(
      deltaSeconds,
    );

    this.spotDensity.update(
      deltaSeconds,
    );

    this.renderer.render(this.scene, this.camera);

    this.animationFrameId = window.requestAnimationFrame(this.render);
  };
}
