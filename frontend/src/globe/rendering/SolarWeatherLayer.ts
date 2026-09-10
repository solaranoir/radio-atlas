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

export class SolarWeatherLayer {
  readonly group = new THREE.Group();

  private readonly activityHalo:
    THREE.Mesh<
      THREE.SphereGeometry,
      THREE.MeshBasicMaterial
    >;

  private readonly auroraGeometry =
    new THREE.CircleGeometry(
      AURORA_RADIUS,
      24,
    );

  private readonly auroraGroup =
    new THREE.Group();

  private readonly auroraMaterial =
    new THREE.MeshBasicMaterial({
      color: 0x66ff99,
      transparent: true,
      opacity: 0.08,
      blending: THREE.AdditiveBlending,
      depthTest: true,
      depthWrite: false,
      side: THREE.DoubleSide,
      vertexColors: false,
    });

  private auroraMesh:
    THREE.InstancedMesh<
      THREE.CircleGeometry,
      THREE.MeshBasicMaterial
    > | null = null;

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
    this.clearAurora();

    this.auroraGeometry.dispose();
    this.auroraMaterial.dispose();

    this.activityHalo.geometry.dispose();
    this.activityHalo.material.dispose();

    this.auroraGroup.clear();
  }

  private renderAurora(
    observations: AuroraObservation[],
  ): void {
    this.clearAurora();

    if (observations.length === 0) {
      return;
    }

    const mesh =
      new THREE.InstancedMesh(
        this.auroraGeometry,
        this.auroraMaterial,
        observations.length,
      );

    const surfaceNormal =
      new THREE.Vector3();

    const geometryNormal =
      new THREE.Vector3(0, 0, 1);

    const dummy =
      new THREE.Object3D();

    for (
      let index = 0;
      index < observations.length;
      index += 1
    ) {
      const observation =
        observations[index];

      const intensity =
        normalizeAuroraIntensity(
          observation.intensity,
        );

      const visuals =
        mapAuroraVisuals(
          intensity,
        );

      const position =
        geographicToGlobeCoordinates(
          {
            latitude:
              observation.latitude,
            longitude:
              observation.longitude,
          },
          EARTH_RADIUS + AURORA_SURFACE_OFFSET,
        );

      surfaceNormal
        .copy(position)
        .normalize();

      dummy.position.copy(position);

      dummy.quaternion.setFromUnitVectors(
        geometryNormal,
        surfaceNormal,
      );

      dummy.scale.setScalar(
          visuals.scale,
      );

      dummy.updateMatrix();

      mesh.setMatrixAt(
        index,
        dummy.matrix,
      );
    }

    mesh.instanceMatrix.needsUpdate =
      true;

    mesh.computeBoundingSphere();

    this.auroraMesh = mesh;
    this.auroraGroup.add(mesh);
  }

  private clearAurora(): void {
    if (
      this.auroraMesh === null
    ) {
      return;
    }

    this.auroraGroup.remove(
      this.auroraMesh,
    );

    this.auroraMesh.dispose();

    this.auroraMesh = null;
  }
}
