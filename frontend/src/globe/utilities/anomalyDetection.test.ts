import {
  describe,
  expect,
  it,
} from "vitest";

import type {
  RadioObservation,
} from "../../api/observations";
import {
  detectAnomalies,
} from "./anomalyDetection";

function createObservation(
  overrides:
    Partial<RadioObservation> = {},
): RadioObservation {
  return {
    id: 1,
    provider_id: 2,
    sequence_number: 123,

    sender_callsign: "TEST1",
    receiver_callsign: "TEST2",

    sender_grid: "DM26",
    receiver_grid: "JN39",

    frequency_hz:
      14_074_000,

    band: "20m",
    mode: "FT8",

    snr_db: 5,

    observed_at:
      "2026-09-01T20:00:00Z",

    transmitted_at:
      "2026-09-01T19:59:45Z",

    ...overrides,
  };
}

describe("detectAnomalies", () => {
  it("detects strong long-distance contacts", () => {
    const anomalies =
      detectAnomalies([
        createObservation(),
      ]);

    expect(
      anomalies.length,
    ).toBeGreaterThan(0);
  });

  it("ignores observations without grids", () => {
    expect(
      detectAnomalies([
        createObservation({
          receiver_grid: null,
        }),
      ]),
    ).toEqual([]);
  });

  it("does not flag ordinary nearby contacts", () => {
    expect(
      detectAnomalies([
        createObservation({
          sender_grid: "DM26",
          receiver_grid: "DM25",
          snr_db: -20,
        }),
      ]),
    ).toEqual([]);
  });
});
