// @vitest-environment jsdom

import {
  cleanup,
  render,
  screen,
} from "@testing-library/react";
import {
  afterEach,
  describe,
  expect,
  it,
} from "vitest";

import type {
  GlobeSelection,
} from "../types/globeSelection";

import {
  InformationPanel,
} from "./InformationPanel";

afterEach(() => {
  cleanup();
});

describe("InformationPanel", () => {
  it("renders summary information with no selection", () => {
    render(
      <InformationPanel
        selection={null}
        observationCount={42}
        anomalyCount={3}
      />,
    );

    expect(
      screen.getByText("Current view"),
    ).toBeTruthy();

    expect(
      screen.getByText("42"),
    ).toBeTruthy();

    expect(
      screen.getByText("3"),
    ).toBeTruthy();

    expect(
      screen.getByText(
        /select a station or signal path/i,
      ),
    ).toBeTruthy();
  });

  it("renders station details when a station is selected", () => {
    const selection: GlobeSelection = {
      kind: "station",
      station: {
        id: "las-vegas",
        callsign: "LAS-VEGAS",
        latitude: 36.1699,
        longitude: -115.1398,
      },
    };

    render(
      <InformationPanel
        selection={selection}
        observationCount={10}
        anomalyCount={1}
      />,
    );

    expect(
      screen.getByText("LAS-VEGAS"),
    ).toBeTruthy();

    expect(
      screen.getByText("36.1699"),
    ).toBeTruthy();

    expect(
      screen.getByText("-115.1398"),
    ).toBeTruthy();
  });

  it("renders signal path details when a path is selected", () => {
    const selection: GlobeSelection = {
      kind: "signal-path",
      path: {
        id: "test-path",
        source: {
          latitude: 36.1699,
          longitude: -115.1398,
        },
        target: {
          latitude: 40.7128,
          longitude: -74.006,
        },
        strength: 0.6,
      },
    };

    render(
      <InformationPanel
        selection={selection}
        observationCount={10}
        anomalyCount={1}
      />,
    );

    expect(
      screen.getByText("Propagation route"),
    ).toBeTruthy();

    expect(
      screen.getByText("60%"),
    ).toBeTruthy();

    expect(
      screen.getByText(
        "36.17, -115.14",
      ),
    ).toBeTruthy();

    expect(
      screen.getByText(
        "40.71, -74.01",
      ),
    ).toBeTruthy();
  });
});
