import {
  useEffect,
  useState,
} from "react";

import {
  fetchObservations,
} from "../../api/observations";
import type {
  Anomaly,
} from "../types/anomaly";
import {
  detectAnomalies,
} from "../utilities/anomalyDetection";

export function useAnomalies(): {
  anomalies: Anomaly[];
  error: Error | null;
} {
  const [
    anomalies,
    setAnomalies,
  ] =
    useState<Anomaly[]>([]);

  const [
    error,
    setError,
  ] =
    useState<Error | null>(
      null,
    );

  useEffect(() => {
    let cancelled = false;

    async function load(): Promise<void> {
      try {
        const observations =
          await fetchObservations();

        if (cancelled) {
          return;
        }

        setAnomalies(
          detectAnomalies(
            observations,
          ),
        );
      } catch (cause) {
        if (cancelled) {
          return;
        }

        setError(
          cause instanceof Error
            ? cause
            : new Error(
                "Failed to load anomalies",
              ),
        );
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  return {
    anomalies,
    error,
  };
}
