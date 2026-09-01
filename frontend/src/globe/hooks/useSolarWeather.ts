import {
  useEffect,
  useState,
} from "react";

import { fetchSolarWeatherSnapshot } from "../../api/solarWeather";
import type { SolarWeatherSnapshot } from "../types/solarWeather";

interface SolarWeatherState {
  snapshot: SolarWeatherSnapshot | null;
  error: Error | null;
}

export function useSolarWeather(): SolarWeatherState {
  const [
    snapshot,
    setSnapshot,
  ] = useState<SolarWeatherSnapshot | null>(
    null,
  );

  const [
    error,
    setError,
  ] = useState<Error | null>(
    null,
  );

  useEffect(() => {
    let cancelled = false;

    async function load(): Promise<void> {
      try {
        const result =
          await fetchSolarWeatherSnapshot();

        if (!cancelled) {
          setSnapshot(result);
          setError(null);
        }
      } catch (caught) {
        if (!cancelled) {
          setError(
            caught instanceof Error
              ? caught
              : new Error(
                  "Failed to load solar weather",
                ),
          );
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  return {
    snapshot,
    error,
  };
}
