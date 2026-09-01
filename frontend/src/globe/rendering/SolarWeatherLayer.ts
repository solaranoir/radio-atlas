import * as THREE from "three";

import type {
  AuroraObservation,
  SolarWeatherSnapshot,
} from "../types/solarWeather";
import { normalizeAuroraIntensity } from "../utilities/auroraIntensity";
import { geographicToGlobeCoordinates } from "../utilities/geographicCoordinates";
import { normalizeKpIndex } from "../utilities/solarActivity";
import {
  mapAuroraVisuals,
  mapSolarActivityVisuals,
} from "../utilities/solarWeatherVisuals";
import { EARTH_RADIUS } from "./createEarth";

const AURORA_RADIUS = 0.018;
const AURORA_SURFACE_OFFSET = 0.016;
const HALO_RADIUS = EARTH_RADIUS * 1.025;

type AuroraMarker = THREE.Mesh<
  THREE.CircleGeometry,
  THREE.MeshBasicMaterial
>;

export class SolarWeatherLayer {
  readonly group = new THREE.Group();

  private readonly auroraGroup =
    new THREE.Group();

  private readonly activityHalo:
    THREE.Mesh<
      THREE.SphereGeometry,
      THREE.MeshBasicMaterial
    >;

  constructor() {
    const haloGeometry =
      new THREE.SphereGeometry(
        HALO_RADIUS,
        64,
        32,
      );

    const haloMaterial =
      new THREE.MeshBasicMaterial({
        color: 0x66ffcc,
        transparent: true,
        opacity: 0.04,
        side: THREE.BackSide,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      });

    this.activityHalo =
      new THREE.Mesh(
        haloGeometry,
        haloMaterial,
      );

    this.group.add(
      this.activityHalo,
      this.auroraGroup,
    );
  }

  setSnapshot(
    snapshot: SolarWeatherSnapshot,
  ): void {
    this.renderAurora(
      snapshot.aurora,
    );

    const activity =
      normalizeKpIndex(
        snapshot.indicators.kpIndex,
      );

    const visuals =
      mapSolarActivityVisuals(
        activity,
      );

    this.activityHalo.material.opacity =
      visuals.opacity;

    this.group.userData.snapshot =
      snapshot;
  }

  dispose(): void {
    for (
      const child
      of this.auroraGroup.children
    ) {
      if (
        child instanceof THREE.Mesh
      ) {
        child.geometry.dispose();

        if (
          child.material instanceof
          THREE.Material
        ) {
          child.material.dispose();
        }
      }
    }

    this.auroraGroup.clear();

    this.activityHalo.geometry.dispose();
    this.activityHalo.material.dispose();

    this.group.clear();
  }

  private renderAurora(
    observations: AuroraObservation[],
  ): void {
    this.clearAurora();

    for (
      const observation
      of observations
    ) {
      const marker =
        createAuroraMarker(
          observation,
        );

      this.auroraGroup.add(marker);
    }
  }

  private clearAurora(): void {
    for (
      const child
      of this.auroraGroup.children
    ) {
      if (
        child instanceof THREE.Mesh
      ) {
        child.geometry.dispose();

        if (
          child.material instanceof
          THREE.Material
        ) {
          child.material.dispose();
        }
      }
    }

    this.auroraGroup.clear();
  }
}

function createAuroraMarker(
  observation: AuroraObservation,
): AuroraMarker {
  const intensity =
    normalizeAuroraIntensity(
      observation.intensity,
    );

  const visuals =
    mapAuroraVisuals(
      intensity,
    );

  const geometry =
    new THREE.CircleGeometry(
      AURORA_RADIUS,
      24,
    );

  const material =
    new THREE.MeshBasicMaterial({
      color: 0x66ff99,
      transparent: true,
      opacity: visuals.opacity,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      side: THREE.DoubleSide,
    });

  const marker =
    new THREE.Mesh(
      geometry,
      material,
    );

  const position =
    geographicToGlobeCoordinates(
      {
        latitude:
          observation.latitude,
        longitude:
          observation.longitude,
      },
      EARTH_RADIUS +
        AURORA_SURFACE_OFFSET,
    );

  marker.position.set(
    position.x,
    position.y,
    position.z,
  );

  marker.lookAt(
    marker.position
      .clone()
      .multiplyScalar(2),
  );

  marker.scale.setScalar(
    visuals.scale,
  );

  marker.userData.observation =
    observation;

  return marker;
}
