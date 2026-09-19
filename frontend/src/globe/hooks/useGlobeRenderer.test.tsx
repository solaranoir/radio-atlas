// @vitest-environment jsdom

import { cleanup, render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useRef } from "react";

import type { ObservationVisualization } from "../utilities/observationVisualizationAdapter";
import { GlobeRenderingContext } from "../rendering/GlobeRenderingContext";
import { useGlobeRenderer } from "./useGlobeRenderer";

vi.mock("../rendering/GlobeRenderingContext", () => ({
    GlobeRenderingContext: vi.fn(),
}));

const visualization: ObservationVisualization = {
    signalPaths: [
        {
            id: "observation-101",
            source: {
                latitude: 36.5,
                longitude: -115,
            },
            target: {
                latitude: 41.5,
                longitude: -73,
            },
            strength: 0.55,
        },
    ],
    stations: [
        {
            id: "station-KK7QEA-DM26",
            callsign: "KK7QEA",
            latitude: 36.5,
            longitude: -115,
        },
        {
            id: "station-W1AW-FN31",
            callsign: "W1AW",
            latitude: 41.5,
            longitude: -73,
        },
    ],
    spotDensityRegions: [],
};

const setObservationVisualization = vi.fn();
const dispose = vi.fn();

function TestComponent({
    observationVisualization,
}: {
    observationVisualization: ObservationVisualization;
}) {
    const containerRef = useRef<HTMLDivElement>(null);

    useGlobeRenderer(containerRef, null, [], observationVisualization, null);

    return <div ref={containerRef} />;
}

describe("useGlobeRenderer", () => {
    beforeEach(() => {
        vi.mocked(GlobeRenderingContext).mockImplementation(
            function MockGlobeRenderingContext() {
                return {
                    setSelectionChangeHandler: vi.fn(),
                    setCameraChangeHandler: vi.fn(),
                    setSelection: vi.fn(),
                    setPerformanceSnapshotHandler: vi.fn(),
                    setLayerVisible: vi.fn(),
                    mount: vi.fn(),
                    start: vi.fn(),
                    resize: vi.fn(),
                    setReducedMotion: vi.fn(),
                    setAnomalies: vi.fn(),
                    setObservationVisualization,
                    dispose,
                } as unknown as GlobeRenderingContext;
            },
        );

        vi.stubGlobal(
            "ResizeObserver",
            class {
                observe() {}
                disconnect() {}
            },
        );
    });

    afterEach(() => {
        cleanup();
        vi.clearAllMocks();
        vi.unstubAllGlobals();
    });

    it("forwards observation visualization updates to the rendering context", () => {
        const { rerender } = render(
            <TestComponent observationVisualization={visualization} />,
        );

        expect(setObservationVisualization).toHaveBeenCalledWith(visualization);

        const updatedVisualization: ObservationVisualization = {
            ...visualization,
            signalPaths: [],
            stations: [visualization.stations[0]],
            spotDensityRegions: [],
        };

        rerender(
            <TestComponent observationVisualization={updatedVisualization} />,
        );

        expect(setObservationVisualization).toHaveBeenLastCalledWith(
            updatedVisualization,
        );

        expect(GlobeRenderingContext).toHaveBeenCalledTimes(1);
    });
});
