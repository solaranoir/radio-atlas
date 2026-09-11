import * as THREE from "three";

import type {
  PredictionPath,
} from "../types/predictionPath";
import {
  generateGreatCirclePath,
} from "../utilities/greatCirclePath";
import {
  advanceOpeningDissolve,
} from "../utilities/openingDissolve";
import {
  mapPredictionVisuals,
} from "../utilities/predictionVisuals";

const PREDICTION_RADIUS = 1.035;

interface PredictionPathVisual {
  line: THREE.Line<
    THREE.BufferGeometry,
    THREE.LineDashedMaterial
  >;
  targetOpacity: number;
  state:
    | "appearing"
    | "steady"
    | "disappearing";
}

export class PredictionPathLayer {
  readonly group =
    new THREE.Group();

  private readonly paths =
    new Map<string, PredictionPathVisual>();

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
      visual,
    ] of this.paths) {
      if (!nextIds.has(id)) {
        visual.state =
          "disappearing";
      }
    }

    for (
      const prediction
      of predictions
    ) {
      this.setPath(prediction);
    }
  }

  update(
    deltaSeconds: number,
    reducedMotion = false,
  ): void {

    for (const [
      id,
      visual,
    ] of this.paths) {

     if (reducedMotion) {
        if (
          visual.state ===
            "disappearing"
        ) {
          this.group.remove(
            visual.line,
          );

          visual.line.geometry.dispose();
          visual.line.material.dispose();

          this.paths.delete(id);
          continue;
        }

        visual.line.material.opacity =
          visual.targetOpacity;

        visual.state = "steady";

        continue;
      }

      const result =
        advanceOpeningDissolve(
          visual.line.material.opacity,
          visual.targetOpacity,
          visual.state,
          deltaSeconds,
        );

      visual.line.material.opacity =
        result.opacity;

      if (
        visual.state ===
          "appearing" &&
        result.complete
      ) {
        visual.state = "steady";
      }

      if (
        visual.state ===
          "disappearing" &&
        result.complete
      ) {
        this.group.remove(
          visual.line,
        );

        visual.line.geometry.dispose();
        visual.line.material.dispose();

        this.paths.delete(id);
      }
    }
  }
  dispose(): void {
    for (
      const visual
      of this.paths.values()
    ) {
      visual.line.geometry.dispose();
      visual.line.material.dispose();
    }

    this.paths.clear();
    this.group.clear();
  }

  private setPath(
    prediction: PredictionPath,
  ): void {

    const visuals =
      mapPredictionVisuals(
        prediction.confidence,
      );

    const existing =
      this.paths.get(
        prediction.id,
      );

    if (existing) {
      existing.targetOpacity =
        visuals.opacity;

      existing.state =
        existing.state ===
          "disappearing"
          ? "appearing"
          : existing.state;

      existing.line.material.dashSize =
        0.035 *
        visuals.dashScale;

      existing.line.material.needsUpdate =
        true;

      return;
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

    const material =
      new THREE.LineDashedMaterial({
        color: 0x9ad7ff,
        transparent: true,
        opacity: 0,
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
      {
        line,
        targetOpacity:
          visuals.opacity,
        state: "appearing",
      },
    );


    this.group.add(
      line,
    );
  }
}
