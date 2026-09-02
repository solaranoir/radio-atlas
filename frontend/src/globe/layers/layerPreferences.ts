import type { GlobeLayerId } from "./globeLayer";
import { globeLayerRegistry } from "./layerRegistry";

const STORAGE_KEY = "radio-atlas-layer-preferences";

export type LayerPreferences = Record<GlobeLayerId, boolean>;

export function createDefaultLayerPreferences(): LayerPreferences {
    return Object.fromEntries(
        globeLayerRegistry.map((layer) => [layer.id, layer.defaultVisible]),
    ) as LayerPreferences;
}

export function loadLayerPreferences(
    storage: Pick<Storage, "getItem"> = window.localStorage,
): LayerPreferences {
    const defaults = createDefaultLayerPreferences();

    try {
        const stored = storage.getItem(STORAGE_KEY);

        if (!stored) {
            return defaults;
        }

        const parsed = JSON.parse(stored) as Partial<
            Record<GlobeLayerId, unknown>
        >;

        return Object.fromEntries(
            globeLayerRegistry.map((layer) => [
                layer.id,
                typeof parsed[layer.id] === "boolean"
                    ? parsed[layer.id]
                    : defaults[layer.id],
            ]),
        ) as LayerPreferences;
    } catch {
        return defaults;
    }
}

export function saveLayerPreferences(
    preferences: LayerPreferences,
    storage: Pick<Storage, "setItem"> = window.localStorage,
): void {
    storage.setItem(STORAGE_KEY, JSON.stringify(preferences));
}
