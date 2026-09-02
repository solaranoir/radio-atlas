export type GlobeLayerId =
  | "stations"
  | "signal-paths"
  | "spot-density"
  | "solar-terminator"
  | "solar-weather"
  | "prediction-paths"
  | "anomalies";

export interface GlobeLayerDefinition {
  id: GlobeLayerId;
  label: string;
  order: number;
  defaultVisible: boolean;
}
