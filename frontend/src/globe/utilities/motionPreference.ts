import type {
  MotionPreference,
} from "../state/globeStore";

export function resolveReducedMotion(
  preference: MotionPreference,
  systemPrefersReducedMotion: boolean,
): boolean {
  if (preference === "reduced") {
    return true;
  }

  if (preference === "full") {
    return false;
  }

  return systemPrefersReducedMotion;
}
