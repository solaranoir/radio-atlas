export interface AuroraObservation {
  longitude: number;
  latitude: number;
  intensity: number;
}

export interface SolarIndicators {
  kpIndex: number | null;
  solarFlux: number | null;
  sunspotNumber: number | null;
  solarWindSpeed: number | null;
}

export interface SolarWeatherSnapshot {
  observedAt: string;
  aurora: AuroraObservation[];
  indicators: SolarIndicators;
}
