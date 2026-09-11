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
    <fieldset
      className="motion-preference-control"
    >
      <legend
        className="control-section__heading"
      >
        Animation
      </legend>

      <div className="motion-preference-control__options">
        <label className="motion-preference-control__option">
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

          <span>
            System preference
          </span>
        </label>

        <label className="motion-preference-control__option">
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

          <span>
            Reduce motion
          </span>
        </label>

        <label className="motion-preference-control__option">
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

          <span>
            Full motion
          </span>
        </label>
      </div>
    </fieldset>
  );

}
