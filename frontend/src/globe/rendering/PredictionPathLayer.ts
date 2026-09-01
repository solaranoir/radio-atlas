import * as THREE from "three";

import type {
  PredictionPath,
} from "../types/predictionPath";
import {
  generateGreatCirclePath,
} from "../utilities/greatCirclePath";
import {
  mapPredictionVisuals,
} from "../utilities/predictionVisuals";

const PREDICTION_RADIUS = 1.035;

export class PredictionPathLayer {
  readonly group =
    new THREE.Group();

  private readonly paths =
    new Map<
      string,
      THREE.Line<
        THREE.BufferGeometry,
        THREE.LineDashedMaterial
      >
    >();

  setPaths(
    predictions: PredictionPath[],
  ): void {
    const nextIds =
      new Set(
        predictions.map(
          (prediction) =>
            prediction.id,
        ),
      );

    for (const [
      id,
      line,
    ] of this.paths) {
      if (!nextIds.has(id)) {
        this.group.remove(line);
        line.geometry.dispose();
        line.material.dispose();
        this.paths.delete(id);
      }
    }

    for (
      const prediction
      of predictions
    ) {
      this.setPath(prediction);
    }
  }

  dispose(): void {
    for (
      const line
      of this.paths.values()
    ) {
      line.geometry.dispose();
      line.material.dispose();
    }

    this.paths.clear();
    this.group.clear();
  }

  private setPath(
    prediction: PredictionPath,
  ): void {
    const existing =
      this.paths.get(
        prediction.id,
      );

    if (existing) {
      this.group.remove(
        existing,
      );

      existing.geometry.dispose();
      existing.material.dispose();

      this.paths.delete(
        prediction.id,
      );
    }

    const points =
      generateGreatCirclePath(
        prediction.source,
        prediction.target,
        {
          radius: PREDICTION_RADIUS,
        },
      );

    const geometry =
      new THREE.BufferGeometry()
        .setFromPoints(
          points.map(
            (point) =>
              new THREE.Vector3(
                point.x,
                point.y,
                point.z,
              ),
          ),
        );
    const visuals =
      mapPredictionVisuals(
        prediction.confidence,
      );

    const material =
      new THREE.LineDashedMaterial({
        color: 0x9ad7ff,
        transparent: true,
        opacity:
          visuals.opacity,
        dashSize:
          0.035 *
          visuals.dashScale,
        gapSize: 0.025,
      });

    const line =
      new THREE.Line(
        geometry,
        material,
      );

    line.computeLineDistances();

    this.paths.set(
      prediction.id,
      line,
    );

    this.group.add(
      line,
    );
  }
}
