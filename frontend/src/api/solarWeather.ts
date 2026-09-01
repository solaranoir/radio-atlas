import {
  mapAuroraCoordinates,
} from "../globe/utilities/solarWeatherAdapter";
import type {
  AuroraObservation,
  SolarWeatherSnapshot,
} from "../globe/types/solarWeather";

interface SolarConditionResponse {
  id: number;
  provider_id: number;
  observation_type: string;
  observed_at: string;
  value: number | null;
  unit: string | null;
  data: Record<string, unknown>;
}

interface AuroraCell {
  aurora: number;
  latitude: number;
  longitude: number;
}

interface AuroraData {
  cells?: AuroraCell[];
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000";

export async function fetchSolarWeatherSnapshot(): Promise<SolarWeatherSnapshot> {
  const [
    kpRecords,
    solarFluxRecords,
    sunspotRecords,
    solarWindRecords,
    auroraRecords,
  ] = await Promise.all([
    fetchSolarConditions("kp_index"),
    fetchSolarConditions("solar_flux"),
    fetchSolarConditions("sunspot_number"),
    fetchSolarConditions("solar_wind"),
    fetchSolarConditions("aurora"),
  ]);

  const kp = kpRecords[0];
  const solarFlux = solarFluxRecords[0];
  const sunspot = sunspotRecords[0];
  const solarWind = solarWindRecords[0];
  const aurora = auroraRecords[0];

  return {
    observedAt:
      aurora?.observed_at ??
      kp?.observed_at ??
      new Date().toISOString(),

    aurora: mapAuroraObservations(aurora),

    indicators: {
      kpIndex: kp?.value ?? null,
      solarFlux: solarFlux?.value ?? null,
      sunspotNumber: sunspot?.value ?? null,
      solarWindSpeed:
        solarWind?.value ?? null,
    },
  };
}

async function fetchSolarConditions(
  observationType: string,
): Promise<SolarConditionResponse[]> {
  const url = new URL(
    "/api/v1/solar-conditions",
    API_BASE_URL,
  );

  url.searchParams.set(
    "observation_type",
    observationType,
  );

  url.searchParams.set(
    "limit",
    "1",
  );

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(
      `Failed to fetch ${observationType}: ${response.status}`,
    );
  }

  return response.json() as Promise<
    SolarConditionResponse[]
  >;
}

function mapAuroraObservations(
  record:
    | SolarConditionResponse
    | undefined,
): AuroraObservation[] {
  if (!record) {
    return [];
  }

  const data =
    record.data as AuroraData;

  if (!Array.isArray(data.cells)) {
    return [];
  }

  return mapAuroraCoordinates(
    data.cells.filter(isAuroraCell),
  );
}

function isAuroraCell(
  value: unknown,
): value is AuroraCell {
  if (
    typeof value !== "object" ||
    value === null
  ) {
    return false;
  }

  const cell =
    value as Record<string, unknown>;

  return (
    typeof cell.aurora ===
      "number" &&
    typeof cell.latitude ===
      "number" &&
    typeof cell.longitude ===
      "number"
  );
}

