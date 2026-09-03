import {
  describe,
  expect,
  it,
} from "vitest";

import type {
  RadioObservation,
} from "../../api/observations";
import {
  DEFAULT_GLOBE_FILTERS,
  type GlobeFilters,
} from "./globeFilters";
import {
  filterObservations,
} from "./filterObservations";

const NOW =
  new Date("2026-09-03T16:00:00Z");

function createObservation(
  overrides: Partial<RadioObservation> = {},
): RadioObservation {
  return {
    id: 1,
    provider_id: 1,
    sequence_number: null,
    sender_callsign: "KK7QEA",
    receiver_callsign: "W1AW",
    sender_grid: "DM26",
    receiver_grid: "FN31",
    frequency_hz: 14_074_000,
    band: "20m",
    mode: "FT8",
    snr_db: -10,
    observed_at:
      "2026-09-03T15:30:00Z",
    transmitted_at: null,
    ...overrides,
  };
}

describe("filterObservations", () => {
  it("filters observations by band", () => {
    const observations = [
      createObservation({
        id: 1,
        band: "20m",
      }),
      createObservation({
        id: 2,
        band: "40m",
      }),
    ];

    const filters: GlobeFilters = {
      ...DEFAULT_GLOBE_FILTERS,
      band: "20m",
    };

    const result =
      filterObservations(
        observations,
        filters,
        NOW,
      );

    expect(
      result.map(
        (observation) =>
          observation.id,
      ),
    ).toEqual([1]);
  });

  it("filters observations by mode", () => {
    const observations = [
      createObservation({
        id: 1,
        mode: "FT8",
      }),
      createObservation({
        id: 2,
        mode: "CW",
      }),
    ];

    const filters: GlobeFilters = {
      ...DEFAULT_GLOBE_FILTERS,
      mode: "FT8",
    };

    const result =
      filterObservations(
        observations,
        filters,
        NOW,
      );

    expect(
      result.map(
        (observation) =>
          observation.id,
      ),
    ).toEqual([1]);
  });

  it("filters observations by time range", () => {
    const observations = [
      createObservation({
        id: 1,
        observed_at:
          "2026-09-03T15:30:00Z",
      }),
      createObservation({
        id: 2,
        observed_at:
          "2026-09-03T14:00:00Z",
      }),
    ];

    const result =
      filterObservations(
        observations,
        DEFAULT_GLOBE_FILTERS,
        NOW,
      );

    expect(
      result.map(
        (observation) =>
          observation.id,
      ),
    ).toEqual([1]);
  });

  it("combines multiple filters", () => {
    const observations = [
      createObservation({
        id: 1,
        band: "20m",
        mode: "FT8",
      }),
      createObservation({
        id: 2,
        band: "20m",
        mode: "CW",
      }),
      createObservation({
        id: 3,
        band: "40m",
        mode: "FT8",
      }),
    ];

    const filters: GlobeFilters = {
      ...DEFAULT_GLOBE_FILTERS,
      band: "20m",
      mode: "FT8",
    };

    const result =
      filterObservations(
        observations,
        filters,
        NOW,
      );

    expect(
      result.map(
        (observation) =>
          observation.id,
      ),
    ).toEqual([1]);
  });

  it("excludes invalid timestamps", () => {
    const observations = [
      createObservation({
        observed_at: "invalid",
      }),
    ];

    const result =
      filterObservations(
        observations,
        DEFAULT_GLOBE_FILTERS,
        NOW,
      );

    expect(result).toEqual([]);
  });

  it("excludes future observations", () => {
    const observations = [
      createObservation({
        observed_at:
          "2026-09-03T16:30:00Z",
      }),
    ];

    const result =
      filterObservations(
        observations,
        DEFAULT_GLOBE_FILTERS,
        NOW,
      );

    expect(result).toEqual([]);
  });

  it("does not filter band or mode when they are null", () => {
    const observations = [
      createObservation({
        id: 1,
        band: "20m",
        mode: "FT8",
      }),
      createObservation({
        id: 2,
        band: "40m",
        mode: "CW",
      }),
    ];

    const result =
      filterObservations(
        observations,
        DEFAULT_GLOBE_FILTERS,
        NOW,
      );

    expect(
      result.map(
        (observation) =>
          observation.id,
      ),
    ).toEqual([1, 2]);
  });

  it("filters observations by receiver region", () => {
    const observations = [
      createObservation({
        id: 1,
        sender_grid: "DM26",
        receiver_grid: "JO01",
      }),
      createObservation({
        id: 2,
        sender_grid: "DM26",
        receiver_grid: "DM26",
      }),
    ];

    const filters: GlobeFilters = {
      ...DEFAULT_GLOBE_FILTERS,
      region: "Europe",
    };

    const result =
      filterObservations(
        observations,
        filters,
        NOW,
      );

    expect(
      result.map(
        (observation) =>
          observation.id,
      ),
    ).toEqual([1]);
  });

  it("does not match a region based only on the sender", () => {
    const observations = [
      createObservation({
        id: 1,
        sender_grid: "DM26",
        receiver_grid: "JO01",
      }),
    ];

    const filters: GlobeFilters = {
      ...DEFAULT_GLOBE_FILTERS,
      region: "North America",
    };

    const result =
      filterObservations(
        observations,
        filters,
        NOW,
      );

    expect(result).toEqual([]);
  });

  it("excludes observations without usable grids when filtering by region", () => {
    const observations = [
      createObservation({
        sender_grid: null,
        receiver_grid: null,
      }),
    ];

    const filters: GlobeFilters = {
      ...DEFAULT_GLOBE_FILTERS,
      region: "North America",
    };

    const result =
      filterObservations(
        observations,
        filters,
        NOW,
      );

    expect(result).toEqual([]);
  });
});
