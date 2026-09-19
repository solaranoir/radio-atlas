import { describe, expect, it } from "vitest";

import { adaptObservationsForVisualization } from "./observationVisualizationAdapter";

describe("adaptObservationsForVisualization", () => {
    it("returns empty visualization collections when there are no observations", () => {
        expect(adaptObservationsForVisualization([])).toEqual({
            signalPaths: [],
            stations: [],
            spotDensityRegions: [],
        });
    });

    it("creates a signal path from valid sender and receiver grids", () => {
        const visualization = adaptObservationsForVisualization([
            {
                id: 101,
                provider_id: 1,
                sequence_number: 1001,
                sender_callsign: "KK7QEA",
                receiver_callsign: "W1AW",
                sender_grid: "DM26",
                receiver_grid: "FN31",
                frequency_hz: 14_074_000,
                band: "20m",
                mode: "FT8",
                snr_db: -10,
                observed_at: "2026-09-18T22:00:00Z",
                transmitted_at: null,
            },
        ]);

        expect(visualization.signalPaths).toHaveLength(1);

        expect(visualization.signalPaths[0]).toMatchObject({
            id: "observation-101",
            source: {
                latitude: 36.5,
                longitude: -115,
            },
            target: {
                latitude: 41.5,
                longitude: -73,
            },
        });
    });

    it("skips signal paths without two valid grids", () => {
      const baseObservation = {
        id: 101,
        provider_id: 1,
        sequence_number: 1001,
        sender_callsign: "KK7QEA",
        receiver_callsign: "W1AW",
        sender_grid: "DM26",
        receiver_grid: "FN31",
        frequency_hz: 14_074_000,
        band: "20m",
        mode: "FT8",
        snr_db: -10,
        observed_at: "2026-09-18T22:00:00Z",
        transmitted_at: null,
      };

      const visualization =
        adaptObservationsForVisualization([
          {
            ...baseObservation,
            id: 102,
            sender_grid: null,
          },
          {
            ...baseObservation,
            id: 103,
            receiver_grid: null,
          },
          {
            ...baseObservation,
            id: 104,
            sender_grid: "INVALID",
          },
          {
            ...baseObservation,
            id: 105,
            receiver_grid: "INVALID",
          },
        ]);

      expect(visualization.signalPaths).toEqual([]);
    });

    it("normalizes SNR into signal path strength", () => {
      const baseObservation = {
        id: 101,
        provider_id: 1,
        sequence_number: 1001,
        sender_callsign: "KK7QEA",
        receiver_callsign: "W1AW",
        sender_grid: "DM26",
        receiver_grid: "FN31",
        frequency_hz: 14_074_000,
        band: "20m",
        mode: "FT8",
        snr_db: -10,
        observed_at: "2026-09-18T22:00:00Z",
        transmitted_at: null,
      };

      const visualization =
        adaptObservationsForVisualization([
          {
            ...baseObservation,
            id: 201,
            snr_db: -40,
          },
          {
            ...baseObservation,
            id: 202,
            snr_db: -10,
          },
          {
            ...baseObservation,
            id: 203,
            snr_db: 20,
          },
          {
            ...baseObservation,
            id: 204,
            snr_db: null,
          },
        ]);

      expect(
        visualization.signalPaths.map(
          (path) => path.strength,
        ),
      ).toEqual([
        0,
        0.5,
        1,
        0,
      ]);
    });

    it("creates stations from valid sender and receiver grids", () => {
      const visualization =
        adaptObservationsForVisualization([
          {
            id: 301,
            provider_id: 1,
            sequence_number: 1001,
            sender_callsign: "KK7QEA",
            receiver_callsign: "W1AW",
            sender_grid: "DM26",
            receiver_grid: "FN31",
            frequency_hz: 14_074_000,
            band: "20m",
            mode: "FT8",
            snr_db: -10,
            observed_at: "2026-09-18T22:00:00Z",
            transmitted_at: null,
          },
        ]);

      expect(visualization.stations).toEqual([
        {
          id: "station-KK7QEA-DM26",
          callsign: "KK7QEA",
          latitude: 36.5,
          longitude: -115,
        },
        {
          id: "station-W1AW-FN31",
          callsign: "W1AW",
          latitude: 41.5,
          longitude: -73,
        },
      ]);
    });

    it("creates a station when only one endpoint has a valid grid", () => {
      const visualization =
        adaptObservationsForVisualization([
          {
            id: 401,
            provider_id: 1,
            sequence_number: 1001,
            sender_callsign: "KK7QEA",
            receiver_callsign: "W1AW",
            sender_grid: "DM26",
            receiver_grid: null,
            frequency_hz: 14_074_000,
            band: "20m",
            mode: "FT8",
            snr_db: -10,
            observed_at: "2026-09-18T22:00:00Z",
            transmitted_at: null,
          },
        ]);

      expect(visualization.signalPaths).toEqual([]);

      expect(visualization.stations).toEqual([
        {
          id: "station-KK7QEA-DM26",
          callsign: "KK7QEA",
          latitude: 36.5,
          longitude: -115,
        },
      ]);
    });

    it("calculates spot density from both valid observation endpoints", () => {
      const visualization =
        adaptObservationsForVisualization([
          {
            id: 501,
            provider_id: 1,
            sequence_number: 1001,
            sender_callsign: "KK7QEA",
            receiver_callsign: "W1AW",
            sender_grid: "DM26",
            receiver_grid: "FN31",
            frequency_hz: 14_074_000,
            band: "20m",
            mode: "FT8",
            snr_db: -10,
            observed_at: "2026-09-18T22:00:00Z",
            transmitted_at: null,
          },
        ]);

      expect(
        visualization.spotDensityRegions,
      ).toHaveLength(2);

      expect(
        visualization.spotDensityRegions.map(
          (region) => region.count,
        ),
      ).toEqual([1, 1]);

      expect(
        visualization.spotDensityRegions.map(
          (region) => region.density,
        ),
      ).toEqual([1, 1]);
    });

    it("deduplicates stations with the same callsign and grid", () => {
      const baseObservation = {
        id: 601,
        provider_id: 1,
        sequence_number: 1001,
        sender_callsign: "KK7QEA",
        receiver_callsign: "W1AW",
        sender_grid: "DM26",
        receiver_grid: "FN31",
        frequency_hz: 14_074_000,
        band: "20m",
        mode: "FT8",
        snr_db: -10,
        observed_at: "2026-09-18T22:00:00Z",
        transmitted_at: null,
      };

      const visualization =
        adaptObservationsForVisualization([
          baseObservation,
          {
            ...baseObservation,
            id: 602,
            sequence_number: 1002,
          },
        ]);

      expect(visualization.stations).toHaveLength(2);

      expect(
        visualization.stations.map(
          (station) => station.id,
        ),
      ).toEqual([
        "station-KK7QEA-DM26",
        "station-W1AW-FN31",
      ]);

      expect(visualization.signalPaths).toHaveLength(2);
    });
});
