import type {
  RadioObservation,
} from "../../api/observations";
import type {
  GlobeFilters,
  RadioBand,
  RadioMode,
  Region,
  TimeRange,
} from "./globeFilters";
import {
  maidenheadToCoordinates,
} from "../utilities/maidenhead";
import {
  getRegionForPoint,
} from "./geographicRegion";

const TIME_RANGE_MILLISECONDS: Record<
  TimeRange,
  number
> = {
  "15m": 15 * 60 * 1000,
  "1h": 60 * 60 * 1000,
  "6h": 6 * 60 * 60 * 1000,
  "24h": 24 * 60 * 60 * 1000,
};

function matchesBand(
  observation: RadioObservation,
  band: RadioBand | null,
): boolean {
  if (band === null) {
    return true;
  }

  return observation.band === band;
}

function matchesMode(
  observation: RadioObservation,
  mode: RadioMode | null,
): boolean {
  if (mode === null) {
    return true;
  }

  return observation.mode === mode;
}

function matchesRegion(
  observation: RadioObservation,
  region: Region | null,
): boolean {
  if (region === null) {
    return true;
  }

  if (!observation.receiver_grid) {
    return false;
  }

  const receiver =
    maidenheadToCoordinates(
      observation.receiver_grid,
    );

  if (!receiver) {
    return false;
  }

  return (
    getRegionForPoint(
      receiver,
    ) === region
  );
}

function matchesTimeRange(
  observation: RadioObservation,
  timeRange: TimeRange,
  now: Date,
): boolean {
  const observedAt =
    new Date(observation.observed_at);

  if (
    Number.isNaN(
      observedAt.getTime(),
    )
  ) {
    return false;
  }

  const cutoff =
    now.getTime() -
    TIME_RANGE_MILLISECONDS[
      timeRange
    ];

  return (
    observedAt.getTime() >= cutoff &&
    observedAt.getTime() <=
      now.getTime()
  );
}

export function filterObservations(
  observations: RadioObservation[],
  filters: GlobeFilters,
  now = new Date(),
): RadioObservation[] {
  return observations.filter(
    (observation) =>
      matchesBand(
        observation,
        filters.band,
      ) &&
      matchesMode(
        observation,
        filters.mode,
      ) &&
      matchesRegion(
        observation,
        filters.region,
      ) &&
      matchesTimeRange(
        observation,
        filters.timeRange,
        now,
      ),
  );
}
