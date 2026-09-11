import {
  useEffect,
} from "react";

import {
  loadMotionPreference,
  saveMotionPreference,
} from "../preferences/motionPreferences";
import {
  useGlobeStore,
  type MotionPreference,
} from "../state/globeStore";

export function MotionPreferenceControl() {
  const motionPreference =
    useGlobeStore(
      (state) =>
        state.motionPreference,
    );

  const setMotionPreference =
    useGlobeStore(
      (state) =>
        state.setMotionPreference,
    );

  useEffect(() => {
    setMotionPreference(
      loadMotionPreference(),
    );
  }, [setMotionPreference]);

  function handleChange(
    preference: MotionPreference,
  ): void {
    saveMotionPreference(
      preference,
    );

    setMotionPreference(
      preference,
    );
  }

  return (
    <div
      className="motion-preference-control"
      aria-label="Animation"
    >
      <div className="control-section__heading">
        Animation
      </div>

      <label>
        <input
          type="radio"
          name="motion-preference"
          value="system"
          checked={
            motionPreference ===
            "system"
          }
          onChange={() =>
            handleChange(
              "system",
            )
          }
        />
        System preference
      </label>

      <label>
        <input
          type="radio"
          name="motion-preference"
          value="reduced"
          checked={
            motionPreference ===
            "reduced"
          }
          onChange={() =>
            handleChange(
              "reduced",
            )
          }
        />
        Reduce motion
      </label>

      <label>
        <input
          type="radio"
          name="motion-preference"
          value="full"
          checked={
            motionPreference ===
            "full"
          }
          onChange={() =>
            handleChange(
              "full",
            )
          }
        />
        Full motion
      </label>
    </div>
  );
}
