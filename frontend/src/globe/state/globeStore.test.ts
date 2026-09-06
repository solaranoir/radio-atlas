import {
  beforeEach,
  describe,
  expect,
  it,
} from "vitest";

import {
  createInitialGlobeState,
  useGlobeStore,
} from "./globeStore";

describe("globeStore", () => {
  beforeEach(() => {
    useGlobeStore.setState(
      createInitialGlobeState(),
    );
  });

  it("starts without camera or selection state", () => {
    const state =
      useGlobeStore.getState();

    expect(state.camera).toBeNull();
    expect(state.selection).toBeNull();
    expect(
      state.activeLayers.size,
    ).toBe(0);
  });

  it("stores camera state", () => {
    const camera = {
      position: {
        x: 1,
        y: 2,
        z: 3,
      },
      target: {
        x: 0,
        y: 0,
        z: 0,
      },
    };

    useGlobeStore
      .getState()
      .setCamera(camera);

    expect(
      useGlobeStore.getState().camera,
    ).toEqual(camera);
  });

  it("stores selection state", () => {
    const selection = {
      kind: "station" as const,
      station: {
        id: "vegas",
        callsign: "KK7QEA",
        latitude: 36.1699,
        longitude: -115.1398,
      },
    };

    useGlobeStore
      .getState()
      .setSelection(selection);

    expect(
      useGlobeStore.getState()
        .selection,
    ).toEqual(selection);
  });

  it("activates a globe layer", () => {
    useGlobeStore
      .getState()
      .setLayerActive(
        "stations",
        true,
      );

    expect(
      useGlobeStore
        .getState()
        .activeLayers.has(
          "stations",
        ),
    ).toBe(true);
  });

  it("deactivates a globe layer", () => {
    useGlobeStore
      .getState()
      .setLayerActive(
        "stations",
        true,
      );

    useGlobeStore
      .getState()
      .setLayerActive(
        "stations",
        false,
      );

    expect(
      useGlobeStore
        .getState()
        .activeLayers.has(
          "stations",
        ),
    ).toBe(false);
  });

  it("creates a new active layer set when layer state changes", () => {
    const previousLayers =
      useGlobeStore
        .getState()
        .activeLayers;

    useGlobeStore
      .getState()
      .setLayerActive(
        "stations",
        true,
      );

    const nextLayers =
      useGlobeStore
        .getState()
        .activeLayers;

    expect(
      nextLayers,
    ).not.toBe(previousLayers);

    expect(
      previousLayers.has(
        "stations",
      ),
    ).toBe(false);
  });

  it("resets globe state", () => {
    useGlobeStore
      .getState()
      .setCamera({
        position: {
          x: 1,
          y: 2,
          z: 3,
        },
        target: {
          x: 0,
          y: 0,
          z: 0,
        },
      });

    useGlobeStore
      .getState()
      .setSelection({
        kind: "station",
        station: {
          id: "vegas",
          callsign: "KK7QEA",
          latitude: 36.1699,
          longitude: -115.1398,
        },
      });

    useGlobeStore
      .getState()
      .setLayerActive(
        "stations",
        true,
      );

    useGlobeStore
      .getState()
      .resetGlobeState();

    const state =
      useGlobeStore.getState();

    expect(
      state.camera,
    ).toBeNull();

    expect(
      state.selection,
    ).toBeNull();

    expect(
      state.activeLayers.size,
    ).toBe(0);
  });

  it("starts with the default globe filters", () => {
    expect(
      useGlobeStore.getState()
        .filters,
    ).toEqual({
      band: null,
      mode: null,
      region: null,
      timeRange: "1h",
    });
  });

  it("stores globe filters", () => {
    const filters = {
      band: "20m" as const,
      mode: "FT8" as const,
      region:
        "North America" as const,
      timeRange: "6h" as const,
    };

    useGlobeStore
      .getState()
      .setFilters(filters);

    expect(
      useGlobeStore.getState()
        .filters,
    ).toEqual(filters);
  });

  it("tracks multiple active layers", () => {
    const {
      setLayerActive,
    } = useGlobeStore.getState();

    setLayerActive(
      "stations",
      true,
    );

    setLayerActive(
      "signal-paths",
      true,
    );

    setLayerActive(
      "anomalies",
      true,
    );

    const activeLayers =
      useGlobeStore.getState()
        .activeLayers;

    expect(
      activeLayers.has("stations"),
    ).toBe(true);

    expect(
      activeLayers.has(
        "signal-paths",
      ),
    ).toBe(true);

    expect(
      activeLayers.has("anomalies"),
    ).toBe(true);

    expect(activeLayers.size).toBe(3);
  });

});
