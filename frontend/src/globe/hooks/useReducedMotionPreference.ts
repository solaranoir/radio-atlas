import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useGlobeStore,
} from "../state/globeStore";
import {
  resolveReducedMotion,
} from "../utilities/motionPreference";

const REDUCED_MOTION_QUERY =
  "(prefers-reduced-motion: reduce)";

export function useReducedMotionPreference(): boolean {
  const motionPreference =
    useGlobeStore(
      (state) =>
        state.motionPreference,
    );

  const [
    systemPrefersReducedMotion,
    setSystemPrefersReducedMotion,
  ] = useState(false);

  useEffect(() => {
    const mediaQuery =
      window.matchMedia(
        REDUCED_MOTION_QUERY,
      );

    setSystemPrefersReducedMotion(
      mediaQuery.matches,
    );

    const handleChange = (
      event: MediaQueryListEvent,
    ): void => {
      setSystemPrefersReducedMotion(
        event.matches,
      );
    };

    mediaQuery.addEventListener(
      "change",
      handleChange,
    );

    return () => {
      mediaQuery.removeEventListener(
        "change",
        handleChange,
      );
    };
  }, []);

  return useMemo(
    () =>
      resolveReducedMotion(
        motionPreference,
        systemPrefersReducedMotion,
      ),
    [
      motionPreference,
      systemPrefersReducedMotion,
    ],
  );
}
