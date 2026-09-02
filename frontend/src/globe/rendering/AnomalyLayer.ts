import * as THREE from "three";

import type {
  Anomaly,
} from "../types/anomaly";
import {
  geographicToGlobeCoordinates,
} from "../utilities/geographicCoordinates";
import {
  mapAnomalyVisuals,
} from "../utilities/anomalyVisuals";

const EARTH_RADIUS = 1;
const ANOMALY_OFFSET = 0.02;
const CORE_RADIUS = 0.018;
const RING_RADIUS = 0.03;

interface AnomalyVisual {
  group: THREE.Group;
  core: THREE.Mesh<
    THREE.CircleGeometry,
    THREE.MeshBasicMaterial
  >;
  ring: THREE.Mesh<
    THREE.RingGeometry,
    THREE.MeshBasicMaterial
  >;
  severity: number;
  phase: number;
}

export class AnomalyLayer {
  readonly group =
    new THREE.Group();

  private readonly anomalies =
    new Map<
      string,
      AnomalyVisual
    >();

  setAnomalies(
    anomalies: Anomaly[],
  ): void {
    const nextIds =
      new Set(
        anomalies.map(
          (anomaly) =>
            anomaly.id,
        ),
      );

    for (const [
      id,
      visual,
    ] of this.anomalies) {
      if (!nextIds.has(id)) {
        this.removeVisual(
          id,
          visual,
        );
      }
    }

    for (
      const anomaly
      of anomalies
    ) {
      this.setAnomaly(
        anomaly,
      );
    }
  }

  update(
    elapsedSeconds: number,
  ): void {
    for (
      const visual
      of this.anomalies.values()
    ) {
      const visuals =
        mapAnomalyVisuals(
          visual.severity,
        );

      const cycle =
        (
          elapsedSeconds *
            visuals.pulseSpeed +
          visual.phase
        ) % 1;

      const pulse =
        Math.sin(
          cycle *
            Math.PI,
        );

      visual.core.scale.setScalar(
        visuals.scale *
          (
            0.9 +
            pulse * 0.2
          ),
      );

      visual.ring.scale.setScalar(
        visuals.scale *
          (
            0.8 +
            cycle * 1.4
          ),
      );

      visual.ring.material.opacity =
        visuals.opacity *
        (
          1 - cycle
        ) *
        0.75;
    }
  }

  dispose(): void {
    for (
      const visual
      of this.anomalies.values()
    ) {
      this.disposeVisual(
        visual,
      );
    }

    this.anomalies.clear();
    this.group.clear();
  }

  private setAnomaly(
    anomaly: Anomaly,
  ): void {
    const existing =
      this.anomalies.get(
        anomaly.id,
      );

    if (existing) {
      this.removeVisual(
        anomaly.id,
        existing,
      );
    }

    const visuals =
      mapAnomalyVisuals(
        anomaly.severity,
      );

    const position =
      geographicToGlobeCoordinates(
        anomaly.location,
        EARTH_RADIUS +
          ANOMALY_OFFSET,
      );

    const container =
      new THREE.Group();

    container.position.set(
      position.x,
      position.y,
      position.z,
    );

    container.lookAt(
      position.x * 2,
      position.y * 2,
      position.z * 2,
    );

    const coreGeometry =
      new THREE.CircleGeometry(
        CORE_RADIUS,
        24,
      );

    const coreMaterial =
      new THREE.MeshBasicMaterial({
        color: 0xff6b35,
        transparent: true,
        opacity:
          visuals.opacity,
        blending:
          THREE.AdditiveBlending,
        depthWrite: false,
        side:
          THREE.DoubleSide,
      });

    const core =
      new THREE.Mesh(
        coreGeometry,
        coreMaterial,
      );

    const ringGeometry =
      new THREE.RingGeometry(
        RING_RADIUS * 0.75,
        RING_RADIUS,
        32,
      );

    const ringMaterial =
      new THREE.MeshBasicMaterial({
        color: 0xffa24c,
        transparent: true,
        opacity:
          visuals.opacity * 0.6,
        blending:
          THREE.AdditiveBlending,
        depthWrite: false,
        side:
          THREE.DoubleSide,
      });

    const ring =
      new THREE.Mesh(
        ringGeometry,
        ringMaterial,
      );

    container.add(
      core,
      ring,
    );

    this.group.add(
      container,
    );

    this.anomalies.set(
      anomaly.id,
      {
        group:
          container,
        core,
        ring,
        severity:
          anomaly.severity,
        phase:
          Math.random(),
      },
    );
  }

  private removeVisual(
    id: string,
    visual: AnomalyVisual,
  ): void {
    this.group.remove(
      visual.group,
    );

    this.disposeVisual(
      visual,
    );

    this.anomalies.delete(
      id,
    );
  }

  private disposeVisual(
    visual: AnomalyVisual,
  ): void {
    visual.core.geometry.dispose();
    visual.core.material.dispose();

    visual.ring.geometry.dispose();
    visual.ring.material.dispose();
  }
}
