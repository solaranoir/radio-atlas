import {
  describe,
  expect,
  it,
} from "vitest";

import {
  loadMotionPreference,
  saveMotionPreference,
} from "./motionPreferences";

describe(
  "motionPreferences",
  () => {
    it(
      "returns system when no preference is stored",
      () => {
        const storage = {
          getItem: () => null,
        };

        expect(
          loadMotionPreference(
            storage,
          ),
        ).toBe("system");
      },
    );

    it(
      "loads a valid stored preference",
      () => {
        const storage = {
          getItem: () =>
            "reduced",
        };

        expect(
          loadMotionPreference(
            storage,
          ),
        ).toBe("reduced");
      },
    );

    it(
      "falls back to system for an invalid stored value",
      () => {
        const storage = {
          getItem: () =>
            "turbo",
        };

        expect(
          loadMotionPreference(
            storage,
          ),
        ).toBe("system");
      },
    );

    it(
      "falls back to system when storage access fails",
      () => {
        const storage = {
          getItem: () => {
            throw new Error(
              "storage unavailable",
            );
          },
        };

        expect(
          loadMotionPreference(
            storage,
          ),
        ).toBe("system");
      },
    );

    it(
      "saves the selected preference",
      () => {
        let savedKey = "";
        let savedValue = "";

        const storage = {
          setItem: (
            key: string,
            value: string,
          ) => {
            savedKey = key;
            savedValue = value;
          },
        };

        saveMotionPreference(
          "full",
          storage,
        );

        expect(
          savedKey,
        ).toBe(
          "radio-atlas-motion-preference",
        );

        expect(
          savedValue,
        ).toBe("full");
      },
    );
  },
);
