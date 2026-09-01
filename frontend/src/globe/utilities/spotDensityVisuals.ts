export interface SpotDensityVisuals {
  opacity: number;
  pulseAmplitude: number;
  pulseSpeed: number;
}

const MIN_OPACITY = 0.25;
const MAX_OPACITY = 0.8;

const MIN_PULSE_AMPLITUDE = 0.05;
const MAX_PULSE_AMPLITUDE = 0.3;

const MIN_PULSE_SPEED = 1;
const MAX_PULSE_SPEED = 3;

export function mapSpotDensityVisuals(
  density: number,
): SpotDensityVisuals {
  const normalizedDensity = Math.max(
    0,
    Math.min(1, density),
  );

  return {
    opacity:
      MIN_OPACITY +
      normalizedDensity *
        (MAX_OPACITY - MIN_OPACITY),

    pulseAmplitude:
      MIN_PULSE_AMPLITUDE +
      normalizedDensity *
        (
          MAX_PULSE_AMPLITUDE -
          MIN_PULSE_AMPLITUDE
        ),

    pulseSpeed:
      MIN_PULSE_SPEED +
      normalizedDensity *
        (
          MAX_PULSE_SPEED -
          MIN_PULSE_SPEED
        ),
  };
}
