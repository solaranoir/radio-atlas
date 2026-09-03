import type {
  GlobeSelection,
} from "../types/globeSelection";

import {
  PathCard,
} from "./PathCard";
import {
  StationCard,
} from "./StationCard";
import {
  SummaryCard,
} from "./SummaryCard";

interface InformationPanelProps {
  selection: GlobeSelection;
  observationCount: number;
  anomalyCount: number;
}

export function InformationPanel({
  selection,
  observationCount,
  anomalyCount,
}: InformationPanelProps) {
  return (
    <div className="information-panel">
      <h2>Information</h2>

      <SummaryCard
        observationCount={
          observationCount
        }
        anomalyCount={anomalyCount}
      />

      {selection === null && (
        <p className="information-panel__empty">
          Select a station or signal
          path to view details.
        </p>
      )}

      {selection?.kind ===
        "station" && (
        <StationCard
          station={
            selection.station
          }
        />
      )}

      {selection?.kind ===
        "signal-path" && (
        <PathCard
          path={selection.path}
        />
      )}
    </div>
  );
}
