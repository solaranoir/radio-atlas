import * as THREE from "three";

import type { Station } from "../types/station";
import { createStationMarker } from "./createStationMarker";

type StationMarker = ReturnType<typeof createStationMarker>;

export class StationCollection {
    readonly group = new THREE.Group();

    private readonly markers = new Map<string, StationMarker>();

    setStations(stations: Station[]): void {
        const incomingIds = new Set(stations.map((station) => station.id));

        for (const station of stations) {
            const existingMarker = this.markers.get(station.id);

            if (existingMarker !== undefined) {
                this.updateMarker(existingMarker, station);
                continue;
            }

            const marker = createStationMarker(station);

            this.markers.set(station.id, marker);

            this.group.add(marker);
        }

        for (const [id, marker] of this.markers) {
            if (incomingIds.has(id)) {
                continue;
            }

            this.group.remove(marker);
            marker.geometry.dispose();
            marker.material.dispose();
            this.markers.delete(id);
        }
    }

    dispose(): void {
        for (const marker of this.markers.values()) {
            marker.geometry.dispose();
            marker.material.dispose();
        }

        this.markers.clear();
        this.group.clear();
    }

    private updateMarker(marker: StationMarker, station: Station): void {
        const replacement = createStationMarker(station);

        marker.position.copy(replacement.position);

        marker.userData.station = station;

        replacement.geometry.dispose();
        replacement.material.dispose();
    }
}
