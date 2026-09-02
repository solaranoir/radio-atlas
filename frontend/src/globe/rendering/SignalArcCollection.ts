import * as THREE from "three";

import type { SignalPath } from "../types/signalPath";
import {
  createSignalArc,
  updateSignalArc,
} from "./createSignalArc";

const OPACITY_CHANGE_RATE = 1.5;

type SignalArc = ReturnType<
  typeof createSignalArc
>;

export class SignalArcCollection {
  readonly group = new THREE.Group();

  private readonly arcs = new Map<
    string,
    SignalArc
  >();

  setPaths(paths: SignalPath[]): void {
    const incomingIds = new Set(
      paths.map((path) => path.id),
    );

    for (const path of paths) {
      const existingArc = this.arcs.get(path.id);

      if (existingArc !== undefined) {
        updateSignalArc(existingArc, path);
        continue;
      }

      const arc = createSignalArc(path);

      this.arcs.set(path.id, arc);
      this.group.add(arc);
    }

    for (const [id, arc] of this.arcs) {
      if (incomingIds.has(id)) {
        continue;
      }

      this.group.remove(arc);

      arc.geometry.dispose();
      arc.material.dispose();

      this.arcs.delete(id);
    }
  }

  update(deltaSeconds: number): void {
    for (const arc of this.arcs.values()) {
      if (
        arc.userData.isSelected ===
        true
      ) {
        continue;
      }

      const targetOpacity =
        arc.userData.targetOpacity as
          | number
          | undefined;

      if (
        targetOpacity === undefined
      ) {
        continue;
      }

      const currentOpacity =
        arc.material.opacity;

      const difference =
        targetOpacity - currentOpacity;

      if (Math.abs(difference) < 0.001) {
        arc.material.opacity =
          targetOpacity;

        continue;
      }

      const maximumChange =
        OPACITY_CHANGE_RATE *
        deltaSeconds;

      const change =
        Math.sign(difference) *
        Math.min(
          Math.abs(difference),
          maximumChange,
        );

      arc.material.opacity +=
        change;
    }
  }

  dispose(): void {
    for (const arc of this.arcs.values()) {
      arc.geometry.dispose();
      arc.material.dispose();
    }

    this.arcs.clear();
    this.group.clear();
  }
}
