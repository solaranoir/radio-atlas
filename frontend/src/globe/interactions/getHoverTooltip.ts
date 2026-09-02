import type * as THREE from "three";

import type { SignalPath } from "../types/signalPath";
import type { Station } from "../types/station";

export interface HoverTooltip {
  title: string;
  details: string[];
}

export function getHoverTooltip(
  object: THREE.Object3D,
): HoverTooltip | null {
  const station =
    object.userData.station as
      | Station
      | undefined;

  if (station) {
    return {
      title: station.callsign,
      details: [
        `${station.latitude.toFixed(2)}°, ${station.longitude.toFixed(2)}°`,
      ],
    };
  }

  const signalPath =
    object.userData.signalPath as
      | SignalPath
      | undefined;

  if (signalPath) {
    return {
      title: "Signal path",
      details: [
        `${formatCoordinates(signalPath.source)} → ${formatCoordinates(signalPath.target)}`,
        `Strength: ${signalPath.strength.toFixed(2)}`,
      ],
    };
  }

  return null;
}

function formatCoordinates(
  coordinates: {
    latitude: number;
    longitude: number;
  },
): string {
  return (
    `${coordinates.latitude.toFixed(2)}°, ` +
    `${coordinates.longitude.toFixed(2)}°`
  );
}
