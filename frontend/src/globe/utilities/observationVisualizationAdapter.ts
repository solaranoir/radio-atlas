import type { RadioObservation } from "../../api/observations";
import type { RadioObservation as GeographicObservation } from "../types/radioObservation";
import type { SignalPath } from "../types/signalPath";
import type { SpotDensityRegion } from "../types/spotDensity";
import type { Station } from "../types/station";
import { maidenheadToCoordinates } from "./maidenhead";
import { calculateSpotDensity } from "./spotDensity";

export interface ObservationVisualization {
    signalPaths: SignalPath[];
    stations: Station[];
    spotDensityRegions: SpotDensityRegion[];
}

function normalizeSignalStrength(snrDb: number | null): number {
    if (snrDb === null) {
        return 0;
    }

    return Math.max(0, Math.min(1, (snrDb + 30) / 40));
}

export function adaptObservationsForVisualization(
    observations: RadioObservation[],
): ObservationVisualization {
    const signalPaths: SignalPath[] = [];
    const stationsById = new Map<string, Station>();
    const densityObservations: GeographicObservation[] = [];

    for (const observation of observations) {
        const senderCoordinates =
            observation.sender_grid === null
                ? null
                : maidenheadToCoordinates(observation.sender_grid);

        const receiverCoordinates =
            observation.receiver_grid === null
                ? null
                : maidenheadToCoordinates(observation.receiver_grid);

        if (observation.sender_grid !== null && senderCoordinates !== null) {
            const id = `station-${observation.sender_callsign}-${observation.sender_grid}`;

            stationsById.set(id, {
                id,
                callsign: observation.sender_callsign,
                latitude: senderCoordinates.latitude,
                longitude: senderCoordinates.longitude,
            });

            densityObservations.push({
                id: `sender-${observation.id}`,
                latitude: senderCoordinates.latitude,
                longitude: senderCoordinates.longitude,
            });
        }

        if (
            observation.receiver_grid !== null &&
            receiverCoordinates !== null
        ) {
            const id = `station-${observation.receiver_callsign}-${observation.receiver_grid}`;

            stationsById.set(id, {
                id,
                callsign: observation.receiver_callsign,
                latitude: receiverCoordinates.latitude,
                longitude: receiverCoordinates.longitude,
            });

            densityObservations.push({
                id: `receiver-${observation.id}`,
                latitude: receiverCoordinates.latitude,
                longitude: receiverCoordinates.longitude,
            });
        }

        if (senderCoordinates === null || receiverCoordinates === null) {
            continue;
        }

        signalPaths.push({
            id: `observation-${observation.id}`,
            source: senderCoordinates,
            target: receiverCoordinates,
            strength: normalizeSignalStrength(observation.snr_db),
        });
    }

    return {
        signalPaths,
        stations: [...stationsById.values()],
        spotDensityRegions: calculateSpotDensity(densityObservations),
    };
}
