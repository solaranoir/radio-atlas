export type AnimationSemantic =
  | "density-pulse"
  | "strength-brightness"
  | "opening-dissolve"
  | "terminator-sweep"
  | "anomaly-flare";

export interface AnimationSemanticDefinition {
  semantic: AnimationSemantic;
  communicates: string;
}

export const ANIMATION_SEMANTICS: ReadonlyArray<
  AnimationSemanticDefinition
> = [
  {
    semantic: "density-pulse",
    communicates: "spot density",
  },
  {
    semantic: "strength-brightness",
    communicates: "signal strength",
  },
  {
    semantic: "opening-dissolve",
    communicates: "propagation opening state",
  },
  {
    semantic: "terminator-sweep",
    communicates: "solar terminator movement",
  },
  {
    semantic: "anomaly-flare",
    communicates: "anomaly severity",
  },
];
