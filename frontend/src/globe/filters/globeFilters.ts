export const RADIO_BANDS = [
  "160m",
  "80m",
  "60m",
  "40m",
  "30m",
  "20m",
  "17m",
  "15m",
  "12m",
  "10m",
  "6m",
] as const;

export type RadioBand =
  (typeof RADIO_BANDS)[number];

export const RADIO_MODES = [
  "FT8",
  "FT4",
  "CW",
  "SSB",
  "RTTY",
] as const;

export type RadioMode =
  (typeof RADIO_MODES)[number];

export const REGIONS = [
  "North America",
  "South America",
  "Europe",
  "Africa",
  "Asia",
  "Oceania",
] as const;

export type Region =
  (typeof REGIONS)[number];

export const TIME_RANGES = [
  "15m",
  "1h",
  "6h",
  "24h",
] as const;

export type TimeRange =
  (typeof TIME_RANGES)[number];

export interface GlobeFilters {
  band: RadioBand | null;
  mode: RadioMode | null;
  region: Region | null;
  timeRange: TimeRange;
}

export const DEFAULT_GLOBE_FILTERS: GlobeFilters = {
  band: null,
  mode: null,
  region: null,
  timeRange: "1h",
};
