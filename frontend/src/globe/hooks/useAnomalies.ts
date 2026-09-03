import {
  useMemo,
} from "react";

import type {
  RadioObservation,
} from "../../api/observations";
import type {
  Anomaly,
} from "../types/anomaly";
import {
  detectAnomalies,
} from "../utilities/anomalyDetection";

export function useAnomalies(
  observations: RadioObservation[],
): Anomaly[] {
  return useMemo(
    () =>
      detectAnomalies(
        observations,
      ),
    [observations],
  );
}
