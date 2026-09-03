import {
  useEffect,
  useState,
} from "react";

import {
  fetchObservations,
  type RadioObservation,
} from "../../api/observations";

export function useObservations(): {
  observations: RadioObservation[];
  error: Error | null;
} {
  const [
    observations,
    setObservations,
  ] =
    useState<RadioObservation[]>([]);

  const [
    error,
    setError,
  ] =
    useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load(): Promise<void> {
      try {
        const result =
          await fetchObservations();

        if (cancelled) {
          return;
        }

        setObservations(result);
        setError(null);
      } catch (cause) {
        if (cancelled) {
          return;
        }

        setError(
          cause instanceof Error
            ? cause
            : new Error(
                "Failed to load observations",
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
    observations,
    error,
  };
}
