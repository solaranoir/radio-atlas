import type {
  MotionPreference,
} from "../state/globeStore";

const STORAGE_KEY =
  "radio-atlas-motion-preference";

export function loadMotionPreference(
  storage: Pick<
    Storage,
    "getItem"
  > = window.localStorage,
): MotionPreference {
  try {
    const stored =
      storage.getItem(
        STORAGE_KEY,
      );

    if (
      stored === "system" ||
      stored === "reduced" ||
      stored === "full"
    ) {
      return stored;
    }

    return "system";
  } catch {
    return "system";
  }
}

export function saveMotionPreference(
  preference: MotionPreference,
  storage: Pick<
    Storage,
    "setItem"
  > = window.localStorage,
): void {
  storage.setItem(
    STORAGE_KEY,
    preference,
  );
}
