import {
  DEFAULT_GLOBE_FILTERS,
  RADIO_BANDS,
  RADIO_MODES,
  REGIONS,
  TIME_RANGES,
  type GlobeFilters,
  type RadioBand,
  type RadioMode,
  type Region,
  type TimeRange,
} from "../filters/globeFilters";
import { FilterSelect } from "./FilterSelect";

interface FilterPanelProps {
  filters: GlobeFilters;
  onChange: (filters: GlobeFilters) => void;
}

export function FilterPanel({
  filters,
  onChange,
}: FilterPanelProps) {
  return (
    <section
      className="filter-panel"
      aria-label="Radio activity filters"
    >
      <div className="control-section__heading">
        Filters
      </div>

      <div className="filter-panel__controls">
        <FilterSelect
          id="band-filter"
          label="Band"
          value={filters.band ?? ""}
          options={RADIO_BANDS}
          allLabel="All bands"
          onChange={(value) => {
            onChange({
              ...filters,
              band:
                value === ""
                  ? null
                  : (value as RadioBand),
            });
          }}
        />

        <FilterSelect
          id="mode-filter"
          label="Mode"
          value={filters.mode ?? ""}
          options={RADIO_MODES}
          allLabel="All modes"
          onChange={(value) => {
            onChange({
              ...filters,
              mode:
                value === ""
                  ? null
                  : (value as RadioMode),
            });
          }}
        />

        <FilterSelect
          id="region-filter"
          label="Region"
          value={filters.region ?? ""}
          options={REGIONS}
          allLabel="All regions"
          onChange={(value) => {
            onChange({
              ...filters,
              region:
                value === ""
                  ? null
                  : (value as Region),
            });
          }}
        />

        <FilterSelect
          id="time-filter"
          label="Time"
          value={filters.timeRange}
          options={TIME_RANGES}
          onChange={(value) => {
            onChange({
              ...filters,
              timeRange: value as TimeRange,
            });
          }}
        />
      </div>

      <button
        type="button"
        className="filter-panel__reset"
        onClick={() => {
          onChange(DEFAULT_GLOBE_FILTERS);
        }}
      >
        Reset filters
      </button>
    </section>
  );
}
