import * as THREE from "three";

import type { SpotDensityRegion } from "../types/spotDensity";
import { mapSpotDensityVisuals } from "../utilities/spotDensityVisuals";
import {
  createSpotDensityMarker,
  type SpotDensityMarker,
} from "./createSpotDensityMarker";

export class SpotDensityLayer {
  readonly group = new THREE.Group();

  private readonly markers =
    new Map<
      string,
      SpotDensityMarker
    >();

  setRegions(
    regions: SpotDensityRegion[],
  ): void {
    const incomingIds =
      new Set(
        regions.map(
          (region) => region.id,
        ),
      );

    for (const region of regions) {
      const existingMarker =
        this.markers.get(region.id);

      if (existingMarker !== undefined) {
        this.updateMarker(
          existingMarker,
          region,
        );

        continue;
      }

      const marker =
        createSpotDensityMarker(
          region,
        );

      this.markers.set(
        region.id,
        marker,
      );

      this.group.add(marker);
    }

    for (
      const [id, marker]
      of this.markers
    ) {
      if (incomingIds.has(id)) {
        continue;
      }

      this.group.remove(marker);

      marker.geometry.dispose();
      marker.material.dispose();

      this.markers.delete(id);
    }
  }

  update(deltaSeconds: number): void {
    for (
      const marker
      of this.markers.values()
    ) {
      const elapsedTime =
        (
          marker.userData.elapsedTime as number
        ) + deltaSeconds;

      marker.userData.elapsedTime =
        elapsedTime;

      const baseOpacity =
        marker.userData.baseOpacity as number;

      const pulseAmplitude =
        marker.userData.pulseAmplitude as number;

      const pulseSpeed =
        marker.userData.pulseSpeed as number;

      const pulse =
        (
          Math.sin(
            elapsedTime *
              pulseSpeed,
          ) +
          1
        ) / 2;

      const scale =
        1 +
        pulse *
          pulseAmplitude;

      marker.scale.setScalar(scale);

      marker.material.opacity =
        baseOpacity *
        (
          0.75 +
          0.25 * pulse
        );
    }
  }

  dispose(): void {
    for (
      const marker
      of this.markers.values()
    ) {
      marker.geometry.dispose();
      marker.material.dispose();
    }

    this.markers.clear();
    this.group.clear();
  }

  private updateMarker(
    marker: SpotDensityMarker,
    region: SpotDensityRegion,
  ): void {
    const visuals =
      mapSpotDensityVisuals(
        region.density,
      );

    marker.userData.region =
      region;

    marker.userData.baseOpacity =
      visuals.opacity;

    marker.userData.pulseAmplitude =
      visuals.pulseAmplitude;

    marker.userData.pulseSpeed =
      visuals.pulseSpeed;
  }
}
