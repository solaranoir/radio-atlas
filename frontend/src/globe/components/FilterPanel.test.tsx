// @vitest-environment jsdom

import {
  cleanup,
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  DEFAULT_GLOBE_FILTERS,
  type GlobeFilters,
} from "../filters/globeFilters";
import { FilterPanel } from "./FilterPanel";

afterEach(() => {
  cleanup();
});

describe("FilterPanel", () => {
  it("renders the current filter values", () => {
    render(
      <FilterPanel
        filters={DEFAULT_GLOBE_FILTERS}
        onChange={vi.fn()}
      />,
    );

    const bandSelect =
      screen.getByLabelText<HTMLSelectElement>(
        "Band",
      );

    const modeSelect =
      screen.getByLabelText<HTMLSelectElement>(
        "Mode",
      );

    const regionSelect =
      screen.getByLabelText<HTMLSelectElement>(
        "Region",
      );

    const timeSelect =
      screen.getByLabelText<HTMLSelectElement>(
        "Time",
      );

    expect(bandSelect.value).toBe("");
    expect(modeSelect.value).toBe("");
    expect(regionSelect.value).toBe("");
    expect(timeSelect.value).toBe("1h");
  });


  it("updates the band filter", () => {
    const onChange = vi.fn();

    render(
      <FilterPanel
        filters={DEFAULT_GLOBE_FILTERS}
        onChange={onChange}
      />,
    );

    fireEvent.change(
      screen.getByLabelText("Band"),
      {
        target: {
          value: "20m",
        },
      },
    );

    expect(onChange).toHaveBeenCalledWith({
      ...DEFAULT_GLOBE_FILTERS,
      band: "20m",
    });
  });

  it("updates the mode filter", () => {
    const onChange = vi.fn();

    render(
      <FilterPanel
        filters={DEFAULT_GLOBE_FILTERS}
        onChange={onChange}
      />,
    );

    fireEvent.change(
      screen.getByLabelText("Mode"),
      {
        target: {
          value: "FT8",
        },
      },
    );

    expect(onChange).toHaveBeenCalledWith({
      ...DEFAULT_GLOBE_FILTERS,
      mode: "FT8",
    });
  });

  it("updates the region filter", () => {
    const onChange = vi.fn();

    render(
      <FilterPanel
        filters={DEFAULT_GLOBE_FILTERS}
        onChange={onChange}
      />,
    );

    fireEvent.change(
      screen.getByLabelText("Region"),
      {
        target: {
          value: "Europe",
        },
      },
    );

    expect(onChange).toHaveBeenCalledWith({
      ...DEFAULT_GLOBE_FILTERS,
      region: "Europe",
    });
  });

  it("updates the time filter", () => {
    const onChange = vi.fn();

    render(
      <FilterPanel
        filters={DEFAULT_GLOBE_FILTERS}
        onChange={onChange}
      />,
    );

    fireEvent.change(
      screen.getByLabelText("Time"),
      {
        target: {
          value: "6h",
        },
      },
    );

    expect(onChange).toHaveBeenCalledWith({
      ...DEFAULT_GLOBE_FILTERS,
      timeRange: "6h",
    });
  });

  it("resets the filters", () => {
    const onChange = vi.fn();

    const filters: GlobeFilters = {
      band: "20m",
      mode: "FT8",
      region: "Europe",
      timeRange: "24h",
    };

    render(
      <FilterPanel
        filters={filters}
        onChange={onChange}
      />,
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Reset filters",
      }),
    );

    expect(onChange).toHaveBeenCalledWith(
      DEFAULT_GLOBE_FILTERS,
    );
  });
});
