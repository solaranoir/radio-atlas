import type {
  SignalPath,
} from "./signalPath";
import type {
  Station,
} from "./station";

export type GlobeSelection =
  | {
      kind: "station";
      station: Station;
    }
  | {
      kind: "signal-path";
      path: SignalPath;
    }
  | null;
