// @vitest-environment jsdom

import {
  cleanup,
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
} from "vitest";

import {
  useGlobeStore,
} from "../state/globeStore";
import {
  MotionPreferenceControl,
} from "./MotionPreferenceControl";

beforeEach(() => {
  window.localStorage.clear();

  useGlobeStore.getState()
    .resetGlobeState();
});

afterEach(() => {
  cleanup();
});

describe(
  "MotionPreferenceControl",
  () => {
    it(
      "defaults to the system preference",
      () => {
        render(
          <MotionPreferenceControl />,
        );

        const systemOption =
          screen.getByRole(
            "radio",
            {
              name:
                "System preference",
            },
          ) as HTMLInputElement;

        expect(
          systemOption.checked,
        ).toBe(true);
      },
    );

    it(
      "loads a saved motion preference",
      () => {
        window.localStorage.setItem(
          "radio-atlas-motion-preference",
          "reduced",
        );

        render(
          <MotionPreferenceControl />,
        );

        const reducedOption =
          screen.getByRole(
            "radio",
            {
              name:
                "Reduce motion",
            },
          ) as HTMLInputElement;

        expect(
          reducedOption.checked,
        ).toBe(true);
      },
    );

    it(
      "updates and saves the selected preference",
      () => {
        render(
          <MotionPreferenceControl />,
        );

        fireEvent.click(
          screen.getByRole(
            "radio",
            {
              name:
                "Full motion",
            },
          ),
        );

        expect(
          useGlobeStore
            .getState()
            .motionPreference,
        ).toBe("full");

        expect(
          window.localStorage.getItem(
            "radio-atlas-motion-preference",
          ),
        ).toBe("full");
      },
    );
  },
);
