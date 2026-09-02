import * as THREE from "three";

import {
  OrbitControls,
} from "three/examples/jsm/controls/OrbitControls.js";

import { AnomalyLayer } from "./AnomalyLayer";
import { createAtmosphere } from "./createAtmosphere";
import { createCamera } from "./createCamera";
import { createEarth } from "./createEarth";
import { createLighting } from "./createLighting";
import {
  createNavigationControls,
} from "./createNavigationControls";
import { createRenderer } from "./createRenderer";
import { createStationMarker } from "./createStationMarker";
import { PredictionPathLayer } from "./PredictionPathLayer";
import { SignalArcCollection } from "./SignalArcCollection";
import { SolarTerminatorLayer } from "./SolarTerminatorLayer";
import { SpotDensityLayer } from "./SpotDensityLayer";
import { SolarWeatherLayer } from "./SolarWeatherLayer";
import {
  createRaycaster,
  pointerToNormalizedDeviceCoordinates,
} from "../interactions/createRaycaster";
import type { Anomaly } from "../types/anomaly";
import type { SolarWeatherSnapshot } from "../types/solarWeather";
import type {
  PredictionPath,
} from "../types/predictionPath";
import { calculateSpotDensity } from "../utilities/spotDensity";

export class GlobeRenderingContext {
  private readonly scene: THREE.Scene;
  private readonly camera: THREE.PerspectiveCamera;
  private readonly renderer: THREE.WebGLRenderer;
  private readonly clock = new THREE.Clock();
  private readonly directionalLight:
    THREE.DirectionalLight;

  private readonly anomalies =
    new AnomalyLayer();
  private readonly controls:
    OrbitControls;
  private readonly predictionPaths =
    new PredictionPathLayer();
  private readonly raycaster =
    createRaycaster();
  private readonly signalArcs =
    new SignalArcCollection();
  private readonly spotDensity =
    new SpotDensityLayer();
  private readonly solarTerminator =
    new SolarTerminatorLayer();
  private readonly solarWeather =
    new SolarWeatherLayer();

  private solarUpdateAccumulator = 0;
  private animationFrameId: number | null = null;
  private container: HTMLElement | null = null;
  private handlePointerDown = (
    event: PointerEvent,
  ): void => {
    const pointer =
      pointerToNormalizedDeviceCoordinates(
        event.clientX,
        event.clientY,
        this.renderer.domElement,
      );

    this.raycaster.setFromCamera(
      new THREE.Vector2(
        pointer.x,
        pointer.y,
      ),
      this.camera,
    );

    const intersections =
      this.raycaster.intersectObjects(
        this.scene.children,
        true,
      );

    if (
      intersections.length === 0
    ) {
      console.log(
        "No selectable object hit",
      );

      return;
    }

    console.log(
      "Hit object:",
      intersections[0].object,
    );
  };

  private updateSolarLighting(): void {
    const sunDirection =
      this.solarTerminator
        .getSunDirection();

    this.directionalLight.position
      .copy(sunDirection)
      .multiplyScalar(5);
  }

  constructor() {
    this.scene = new THREE.Scene();
    this.camera = createCamera();
    this.renderer = createRenderer();

    const lighting = createLighting();
    const earth = createEarth();
    const atmosphere = createAtmosphere();

    this.renderer.domElement
      .addEventListener(
        "pointerdown",
        this.handlePointerDown,
      );
 
    this.controls =
      createNavigationControls(
        this.camera,
        this.renderer.domElement,
      );  

    this.directionalLight =
      lighting.directionalLight;
  
    this.scene.add(
      lighting.ambientLight,
      lighting.directionalLight,
    );

    this.scene.add(earth);
    this.scene.add(atmosphere);
    this.scene.add(
      this.solarTerminator.group,
    );
    this.scene.add(
      this.solarWeather.group,
    );
    this.scene.add(
      this.predictionPaths.group,
      this.anomalies.group,
    );

    this.updateSolarLighting();

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
      this.scene.add(
        createStationMarker(station),
      );
    }
  }

  setPredictionPaths(
    predictions: PredictionPath[],
  ): void {
    this.predictionPaths.setPaths(
      predictions,
    );
  }

  setSolarWeatherSnapshot(
    snapshot: SolarWeatherSnapshot,
  ): void {
    this.solarWeather.setSnapshot(
      snapshot,
    );
  }

  setAnomalies(
    anomalies: Anomaly[],
  ): void {
    this.anomalies.setAnomalies(
      anomalies,
    );
  }

  resetCamera(): void {
    this.controls.reset();
    this.controls.update();
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
    this.solarTerminator.dispose();
    this.solarWeather.dispose();
    this.predictionPaths.dispose();
    this.anomalies.dispose();
    this.controls.dispose();
    this.renderer.domElement
      .removeEventListener(
        "pointerdown",
        this.handlePointerDown,
      );
    this.renderer.dispose();
    this.container = null;
  }

  private render = (): void => {
    const deltaSeconds =
      this.clock.getDelta();

    const elapsedSeconds =
      this.clock.elapsedTime;

    this.signalArcs.update(
      deltaSeconds,
    );

    this.spotDensity.update(
      deltaSeconds,
    );

    this.solarUpdateAccumulator +=
      deltaSeconds;

    if (
      this.solarUpdateAccumulator >= 60
    ) {
      this.solarTerminator.update(
        new Date(),
      );

      this.updateSolarLighting();

      this.solarUpdateAccumulator = 0;
    }

    this.anomalies.update(
      elapsedSeconds,
    );

    this.controls.update();

    this.renderer.render(
      this.scene,
      this.camera,
    );

    this.animationFrameId =
      window.requestAnimationFrame(
        this.render,
      );
  };
}
