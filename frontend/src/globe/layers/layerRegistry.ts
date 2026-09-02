import type {
  GlobeLayerDefinition,
  GlobeLayerId,
} from "./globeLayer";

export const globeLayerRegistry:
  readonly GlobeLayerDefinition[] = [
    {
      id: "solar-terminator",
      label: "Solar Terminator",
      order: 10,
      defaultVisible: true,
    },
    {
      id: "solar-weather",
      label: "Solar Weather",
      order: 20,
      defaultVisible: true,
    },
    {
      id: "spot-density",
      label: "Spot Density",
      order: 30,
      defaultVisible: true,
    },
    {
      id: "prediction-paths",
      label: "Prediction Paths",
      order: 40,
      defaultVisible: true,
    },
    {
      id: "signal-paths",
      label: "Signal Paths",
      order: 50,
      defaultVisible: true,
    },
    {
      id: "stations",
      label: "Stations",
      order: 60,
      defaultVisible: true,
    },
    {
      id: "anomalies",
      label: "Anomalies",
      order: 70,
      defaultVisible: true,
    },
  ];

export function getGlobeLayerDefinition(
  id: GlobeLayerId,
): GlobeLayerDefinition {
  const layer =
    globeLayerRegistry.find(
      (candidate) =>
        candidate.id === id,
    );

  if (!layer) {
    throw new Error(
      `Unknown globe layer: ${id}`,
    );
  }

  return layer;
}
