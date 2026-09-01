import type { RadioObservation } from "../types/radioObservation";
import type { SpotDensityRegion } from "../types/spotDensity";

const DEFAULT_CELL_SIZE_DEGREES = 10;

interface DensityCell {
  latitude: number;
  longitude: number;
  count: number;
}

export function calculateSpotDensity(
  observations: RadioObservation[],
  cellSizeDegrees = DEFAULT_CELL_SIZE_DEGREES,
): SpotDensityRegion[] {
  if (cellSizeDegrees <= 0) {
    throw new RangeError(
      "cellSizeDegrees must be greater than 0",
    );
  }

  if (observations.length === 0) {
    return [];
  }

  const cells = new Map<string, DensityCell>();

  for (const observation of observations) {
    const latitude =
      getCellCenter(
        observation.latitude,
        cellSizeDegrees,
      );

    const longitude =
      getCellCenter(
        observation.longitude,
        cellSizeDegrees,
      );

    const id = `${latitude}:${longitude}`;

    const existingCell = cells.get(id);

    if (existingCell !== undefined) {
      existingCell.count += 1;
      continue;
    }

    cells.set(id, {
      latitude,
      longitude,
      count: 1,
    });
  }

  const maximumCount = Math.max(
    ...Array.from(
      cells.values(),
      (cell) => cell.count,
    ),
  );

  return Array.from(
    cells.entries(),
    ([id, cell]) => ({
      id,
      latitude: cell.latitude,
      longitude: cell.longitude,
      count: cell.count,
      density:
        cell.count / maximumCount,
    }),
  );
}

function getCellCenter(
  coordinate: number,
  cellSizeDegrees: number,
): number {
  const cellIndex = Math.floor(
    coordinate / cellSizeDegrees,
  );

  return (
    cellIndex * cellSizeDegrees +
    cellSizeDegrees / 2
  );
}
