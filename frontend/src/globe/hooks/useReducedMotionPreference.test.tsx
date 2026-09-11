// @vitest-environment jsdom

import {
  cleanup,
  render,
  screen,
} from "@testing-library/react";
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  useGlobeStore,
} from "../state/globeStore";
import {
  useReducedMotionPreference,
} from "./useReducedMotionPreference";

function TestComponent() {
  const reducedMotion =
    useReducedMotionPreference();

  return (
    <div>
      {reducedMotion
        ? "reduced"
        : "full"}
    </div>
  );
}

function mockMatchMedia(
  matches: boolean,
): void {
  Object.defineProperty(
    window,
    "matchMedia",
    {
      writable: true,
      value: vi.fn().mockImplementation(
        (query: string) => ({
          matches,
          media: query,
          onchange: null,
          addListener: vi.fn(),
          removeListener: vi.fn(),
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
          dispatchEvent: vi.fn(),
        }),
      ),
    },
  );
}

describe(
  "useReducedMotionPreference",
  () => {
    beforeEach(() => {
      useGlobeStore
        .getState()
        .resetGlobeState();
    });
    afterEach(() => {
      cleanup();
    });


    it(
      "follows the operating system setting when preference is system",
      () => {
        mockMatchMedia(false);

        const { unmount } =
          render(
            <TestComponent />,
          );

        expect(
          screen.getByText("full"),
        ).toBeTruthy();

        unmount();

        mockMatchMedia(true);

        render(
          <TestComponent />,
        );

        expect(
          screen.getByText("reduced"),
        ).toBeTruthy();
      },
    );

    it(
      "forces reduced motion",
      () => {
        mockMatchMedia(false);

        useGlobeStore
          .getState()
          .setMotionPreference(
            "reduced",
          );

        render(
          <TestComponent />,
        );

        expect(
          screen.getByText("reduced"),
        ).toBeTruthy();
      },
    );

    it(
      "forces full motion",
      () => {
        mockMatchMedia(true);

        useGlobeStore
          .getState()
          .setMotionPreference(
            "full",
          );

        render(
          <TestComponent />,
        );

        expect(
          screen.getByText("full"),
        ).toBeTruthy();
      },
    );
  },
);
