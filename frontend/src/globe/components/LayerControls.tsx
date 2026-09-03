import { useEffect, useState } from "react";

import type { GlobeLayerId } from "../layers/globeLayer";
import { globeLayerRegistry } from "../layers/layerRegistry";
import {
    loadLayerPreferences,
    saveLayerPreferences,
    type LayerPreferences,
} from "../layers/layerPreferences";
import { LayerToggle } from "./LayerToggle";

interface LayerControlsProps {
    onVisibilityChange: (id: GlobeLayerId, visible: boolean) => void;
}

export function LayerControls({ onVisibilityChange }: LayerControlsProps) {
    const [preferences, setPreferences] = useState<LayerPreferences>(() => {
        const loaded = loadLayerPreferences();

        console.log("Loaded layer preferences:", loaded);

        return loaded;
    });

    useEffect(() => {
        for (const layer of globeLayerRegistry) {
            onVisibilityChange(layer.id, preferences[layer.id]);
        }
    }, [onVisibilityChange, preferences]);

    function handleChange(id: GlobeLayerId, visible: boolean): void {
        onVisibilityChange(id, visible);

        setPreferences((current) => {
            const next = {
                ...current,
                [id]: visible,
            };

            saveLayerPreferences(next);

            return next;
        });
    }

    return (
          <div
            className="layer-controls"
            aria-label="Layers"
          >
            <div
              className="control-section__heading"
            >
              Layers
            </div>

            <div className="layer-controls__list">
              {globeLayerRegistry.map(
                (layer) => (
                  <LayerToggle
                    key={layer.id}
                    id={layer.id}
                    label={layer.label}
                    checked={
                      preferences[
                        layer.id
                      ]
                    }
                    onChange={
                      handleChange
                    }
                  />
                ),
              )}
            </div>
          </div>
    );
}
