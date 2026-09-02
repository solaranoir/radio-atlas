// @vitest-environment jsdom

import { describe, expect, it, vi } from "vitest";

import {
    createDefaultLayerPreferences,
    loadLayerPreferences,
    saveLayerPreferences,
} from "./layerPreferences";

describe("layerPreferences", () => {
    it("creates preferences from registry defaults", () => {
        const preferences = createDefaultLayerPreferences();

        expect(preferences.stations).toBe(true);

        expect(preferences["signal-paths"]).toBe(true);
    });

    it("loads valid stored preferences", () => {
        const storage = {
            getItem: vi.fn(() =>
                JSON.stringify({
                    stations: false,
                    anomalies: false,
                }),
            ),
        };

        const preferences = loadLayerPreferences(storage);

        expect(preferences.stations).toBe(false);

        expect(preferences.anomalies).toBe(false);

        expect(preferences["signal-paths"]).toBe(true);
    });

    it("falls back to defaults for invalid data", () => {
        const storage = {
            getItem: vi.fn(() => "{invalid"),
        };

        expect(loadLayerPreferences(storage)).toEqual(
            createDefaultLayerPreferences(),
        );
    });

    it("saves preferences", () => {
        const setItem = vi.fn();

        const preferences = createDefaultLayerPreferences();

        preferences.stations = false;

        saveLayerPreferences(preferences, {
            setItem,
        });

        expect(setItem).toHaveBeenCalledWith(
            "radio-atlas-layer-preferences",
            JSON.stringify(preferences),
        );
    });
});
