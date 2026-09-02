// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { LayerToggle } from "./LayerToggle";

afterEach(() => {
    cleanup();
});

describe("LayerToggle", () => {
    it("renders its current state", () => {
        render(
            <LayerToggle
                id="stations"
                label="Stations"
                checked
                onChange={() => {}}
            />,
        );

        const checkbox = screen.getByRole("checkbox", {
            name: "Stations",
        }) as HTMLInputElement;

        expect(checkbox.checked).toBe(true);
    });

    it("reports visibility changes", () => {
        const onChange = vi.fn();

        render(
            <LayerToggle
                id="stations"
                label="Stations"
                checked
                onChange={onChange}
            />,
        );

        fireEvent.click(
            screen.getByRole("checkbox", {
                name: "Stations",
            }),
        );

        expect(onChange).toHaveBeenCalledWith("stations", false);
    });
});
