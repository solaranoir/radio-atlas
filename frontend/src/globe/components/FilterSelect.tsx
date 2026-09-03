interface FilterSelectProps<T extends string> {
  id: string;
  label: string;
  value: T | "";
  options: readonly T[];
  allLabel?: string;
  onChange: (value: T | "") => void;
}

export function FilterSelect<T extends string>({
  id,
  label,
  value,
  options,
  allLabel,
  onChange,
}: FilterSelectProps<T>) {
  return (
    <label
      className="filter-control"
      htmlFor={id}
    >
      <span className="filter-control__label">
        {label}
      </span>

      <select
        id={id}
        className="filter-control__select"
        value={value}
        onChange={(event) => {
          onChange(event.target.value as T | "");
        }}
      >
        {allLabel !== undefined && (
          <option value="">
            {allLabel}
          </option>
        )}

        {options.map((option) => (
          <option
            key={option}
            value={option}
          >
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
