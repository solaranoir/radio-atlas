import type { GlobeLayerId } from "../layers/globeLayer";

interface LayerToggleProps {
    id: GlobeLayerId;
    label: string;
    checked: boolean;
    onChange: (id: GlobeLayerId, visible: boolean) => void;
}

export function LayerToggle({
    id,
    label,
    checked,
    onChange,
}: LayerToggleProps) {
    return (
        <label>
            <input
                type="checkbox"
                checked={checked}
                onChange={(event) => onChange(id, event.target.checked)}
            />

            <span>{label}</span>
        </label>
    );
}
