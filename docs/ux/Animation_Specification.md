# Radio Atlas Animation Specification

## Purpose

Animations in the Radio Weather Globe communicate changes in radio and
environmental conditions. Motion is treated as information, not decoration.

This specification defines the shared timing and interpolation standards used
by the globe rendering system.

## Animation Semantics

| Animation | Meaning |
|---|---|
| Pulse | Spot density |
| Brightness | Signal strength |
| Dissolve | Propagation opening state |
| Sweep | Solar terminator movement |
| Flare | Anomaly severity |

## Transition Durations

Shared transition durations are defined in
`src/globe/utilities/transitionStandards.ts`.

| Name | Duration | Intended Use |
|---|---:|---|
| `quick` | 0.2 seconds | Short visual feedback |
| `standard` | 0.4 seconds | General-purpose transitions |
| `deliberate` | 0.6 seconds | Changes that should remain perceptible |

Prediction-path opening and closing dissolves use the `deliberate`
transition duration.

## Transition Rates

Shared rate-based transitions are also defined in
`src/globe/utilities/transitionStandards.ts`.

| Name | Rate | Intended Use |
|---|---:|---|
| `opacity` | 1.5 units/second | Smooth opacity changes for signal arcs |

Signal-path brightness transitions use the shared opacity rate while their
target opacity remains derived from propagation strength.

## Interpolation

The globe currently uses linear interpolation for shared transition behavior.

Transition progress is clamped to the range `0` through `1`.

Negative elapsed time does not reverse an animation. Progress below `0` is
treated as `0`, and progress above `1` is treated as complete.

A zero-duration transition completes immediately.

## Domain-Driven Animation Timing

Not every animation should use a shared fixed duration.

The following animation characteristics remain domain-driven:

- Spot-density pulse amplitude and speed are derived from density.
- Anomaly scale, opacity, and pulse speed are derived from severity.
- Solar terminator position is derived from time and solar position.
- Signal-path target brightness is derived from propagation strength.

These values should not be replaced with generic transition constants because
their timing and intensity communicate domain information.

## Prediction Opening Lifecycle

Prediction paths use presence in the current prediction set to represent an
active predicted propagation opening.

The lifecycle is:

1. A new prediction begins in the `appearing` state.
2. Its opacity transitions from zero to its confidence-derived target opacity.
3. Once the target opacity is reached, the prediction becomes `steady`.
4. A prediction missing from the next prediction set becomes `disappearing`.
5. Its opacity transitions toward zero.
6. Once fully transparent, its Three.js resources are removed and disposed.

If a disappearing prediction reappears before the dissolve completes, it
returns to the `appearing` state instead of being rebuilt.

Prediction confidence controls the steady-state opacity and dash treatment. It
does not represent opening or closing state.

## Implementation Rules

- Use shared transition constants for presentation timing.
- Keep domain-derived timing and intensity tied to their underlying data.
- Avoid introducing additional animation loops or timers when the existing
  globe render loop can advance the transition.
- Preserve stable object identity during transitions when possible.
- Dispose Three.js geometry and materials after an object has fully left the
  scene.
- Animation behavior should remain testable independently of browser rendering.
