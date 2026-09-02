// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { LayerControls } from "./LayerControls";

afterEach(() => {
    cleanup();
    window.localStorage.clear();
});

describe("LayerControls", () => {
    it("renders registered layers", () => {
        render(<LayerControls onVisibilityChange={() => {}} />);

        expect(
            screen.getByRole("checkbox", {
                name: "Stations",
            }),
        ).toBeTruthy();

        expect(
            screen.getByRole("checkbox", {
                name: "Anomalies",
            }),
        ).toBeTruthy();
    });

    it("reports visibility changes", () => {
        const onVisibilityChange = vi.fn();

        render(<LayerControls onVisibilityChange={onVisibilityChange} />);

        onVisibilityChange.mockClear();

        fireEvent.click(
            screen.getByRole("checkbox", {
                name: "Stations",
            }),
        );

        expect(onVisibilityChange).toHaveBeenCalledWith("stations", false);
    });

    it("restores persisted preferences", () => {
        window.localStorage.setItem(
            "radio-atlas-layer-preferences",
            JSON.stringify({
                stations: false,
            }),
        );

        render(<LayerControls onVisibilityChange={() => {}} />);

        const checkbox = screen.getByRole("checkbox", {
            name: "Stations",
        }) as HTMLInputElement;

        expect(checkbox.checked).toBe(false);
    });
});
