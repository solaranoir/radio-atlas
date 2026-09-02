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
import {
  isClickGesture,
} from "../interactions/isClickGesture";
import type { Anomaly } from "../types/anomaly";
import type { SolarWeatherSnapshot } from "../types/solarWeather";
import type {
  PredictionPath,
} from "../types/predictionPath";
import { calculateSpotDensity } from "../utilities/spotDensity";

function hasMaterial(
  object: THREE.Object3D,
): object is THREE.Object3D & {
  material: THREE.Material;
} {
  return (
    "material" in object &&
    object.material instanceof
      THREE.Material
  );
}

export class GlobeRenderingContext {
  private pointerDownPosition:
    THREE.Vector2 | null = null;
  private readonly scene: THREE.Scene;
  private readonly camera: THREE.PerspectiveCamera;
  private readonly renderer: THREE.WebGLRenderer;
  private readonly clock = new THREE.Clock();
  private readonly directionalLight:
    THREE.DirectionalLight;
  private selectedObject:
    THREE.Object3D | null = null;

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
  private static readonly CLICK_DRAG_THRESHOLD = 5;

  private solarUpdateAccumulator = 0;
  private animationFrameId: number | null = null;
  private container: HTMLElement | null = null;

  private clearSelection(): void {
    if (
      this.selectedObject === null
    ) {
      return;
    }

    const object =
      this.selectedObject;

    if (
      object.userData
        .originalScale
    ) {
      object.scale.copy(
        object.userData
          .originalScale,
      );
    }

    if (
      object instanceof THREE.Line &&
      object.material instanceof
        THREE.LineBasicMaterial
    ) {
      const originalColor =
        object.userData.originalColor;

      if (
        originalColor instanceof
        THREE.Color
      ) {
        object.material.color.copy(
          originalColor,
        );
      }
    }

    if (hasMaterial(object)) {
      const originalOpacity =
        object.userData
          .originalOpacity;

      if (
        typeof originalOpacity ===
        "number"
      ) {
        object.material.opacity =
          originalOpacity;
      }
    }

    this.selectedObject = null;
  }

  private selectSignalPath(
    object: THREE.Object3D,
  ): void {
    if (
      !(
        object instanceof
        THREE.Line
      )
    ) {
      return;
    }

    if (
      !(
        object.material instanceof
        THREE.LineBasicMaterial
      )
    ) {
      return;
    }

    object.userData.originalColor =
      object.material.color.clone();

    object.userData.originalOpacity =
      object.material.opacity;

    object.material.color.set(
      0xffffff,
    );

    object.material.opacity = 1;
  }

  private selectObject(
    object: THREE.Object3D,
  ): void {
    this.clearSelection();

    if (
      object.userData.signalPath
    ) {
      this.selectSignalPath(object);

      this.selectedObject =
        object;

      return;
    }

    object.userData.originalScale =
      object.scale.clone();

    object.scale.multiplyScalar(
      1.35,
    );

    if (hasMaterial(object)) {
      object.userData.originalOpacity =
        object.material.opacity;

      object.material.transparent =
        true;

      object.material.opacity =
        Math.min(
          1,
          object.material.opacity +
            0.25,
        );
    }

    this.selectedObject =
      object;
  }

  private handlePointerDown = (
    event: PointerEvent,
  ): void => {
    this.pointerDownPosition =
      new THREE.Vector2(
        event.clientX,
        event.clientY,
      );
  };

  private handlePointerUp = (
    event: PointerEvent,
  ): void => {
    if (
      this.pointerDownPosition === null
    ) {
      return;
    }

  const start = {
    x: this.pointerDownPosition.x,
    y: this.pointerDownPosition.y,
  };

  const end = {
    x: event.clientX,
    y: event.clientY,
  };

  this.pointerDownPosition = null;

  if (
    !isClickGesture(
      start,
      end,
      GlobeRenderingContext
        .CLICK_DRAG_THRESHOLD,
    )
  ) {
    return;
  }
    this.handleSelection(event);
  };

  private handleSelection(
    event: PointerEvent,
  ): void {
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

    const stationIntersection =
      intersections.find(
        ({ object }) =>
          object.userData.station,
      );

    const signalPathIntersection =
      intersections.find(
        ({ object }) =>
          object.userData.signalPath,
      );

    const selectable =
      stationIntersection ??
      signalPathIntersection;

    if (!selectable) {
      this.clearSelection();

      return;
    }

    this.selectObject(
      selectable.object,
    );
  }

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
    this.renderer.domElement
      .addEventListener(
        "pointerup",
        this.handlePointerUp,
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
    this.renderer.domElement
      .removeEventListener(
        "pointerup",
        this.handlePointerUp,
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
