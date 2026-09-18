# Radio Weather Globe UI Reference

## Purpose

This document records the implemented Phase 2 user-interface structure for the
Radio Weather Globe.

The diagrams represent the functional layout and interaction regions of the
completed interface. They are intended as implementation-reference wireframes
rather than pixel-accurate visual specifications.

## Desktop Layout

The desktop interface organizes the globe as the primary workspace, with
controls and contextual information surrounding it.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Application Header                             │
├──────────────────┬───────────────────────────────────────┬──────────────────┤
│                  │                                       │                  │
│  Filters         │                                       │  Information     │
│                  │                                       │                  │
│  Band            │                                       │  Summary         │
│  Mode            │          RADIO WEATHER GLOBE          │                  │
│  Region          │                                       │  Selected        │
│  Time            │          Interactive WebGL            │  Station / Path  │
│                  │             Workspace                 │                  │
│  Layers          │                                       │  Details         │
│                  │                                       │                  │
│  □ Terminator    │                                       │                  │
│  □ Solar Weather │                                       │                  │
│  □ Spot Density  │                                       │                  │
│  □ Predictions   │                                       │                  │
│  □ Signal Paths  │                                       │                  │
│  □ Stations      │                                       │                  │
│  □ Anomalies     │                                       │                  │
│                  │                                       │                  │
├──────────────────┴───────────────────────────────────────┴──────────────────┤
│                              Bottom Panel                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

The globe remains the dominant visual element. Supporting controls are kept
outside the WebGL canvas so they remain ordinary accessible HTML controls.

## Primary Interface Regions

### Header

The header establishes the Radio Weather Globe application context.

It remains separate from the Three.js canvas and the scientific visualization
layers.

### Filter region

The filter controls allow the user to constrain displayed observation data.

Phase 2 filtering supports:

- band
- mode
- geographic region
- observation time

Filtering changes application data rather than camera position or Three.js
scene navigation.

### Layer controls

Layer controls allow independent visibility management for the globe's
scientific overlays.

The available Phase 2 layers are:

- Solar Terminator
- Solar Weather
- Spot Density
- Prediction Paths
- Signal Paths
- Stations
- Anomalies

Layer choices persist independently from the lifetime of the Three.js
rendering context.

### Globe workspace

The globe workspace contains the WebGL canvas and is the primary interaction
surface.

It supports:

- pointer rotation
- pointer zoom/navigation
- object hover
- station and signal-path selection
- keyboard rotation
- keyboard zoom
- viewport-center selection
- selection clearing
- camera reset

The globe interaction surface is keyboard focusable.

### Information region

The information panel displays application-level information derived from the
current globe state and selection.

It uses specialized presentation components for:

- summary information
- selected stations
- selected signal paths

Selection originates in the Three.js scene but is synchronized into
application state before being presented here.

### Bottom panel

The bottom region provides additional application information without
overlapping the central globe workspace.

It remains part of the normal React layout rather than being rendered into the
Three.js scene.

## Globe Interaction Model

```text
                       ┌─────────────────────────┐
                       │      Globe Canvas       │
                       │                         │
       Rotate ─────────►  Drag / Arrow Keys      │
                       │                         │
       Zoom ───────────►  Navigation / +/-       │
                       │                         │
       Hover ──────────►  Tooltip + Highlight    │
                       │                         │
       Select ─────────►  Click / Enter          │
                       │                         │
       Clear ──────────►  Escape                 │
                       │                         │
       Reset ──────────►  Reset Camera           │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │    Application State    │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │   Information Panel     │
                       └─────────────────────────┘
```

Pointer and keyboard operations ultimately use the same rendering-context
interaction boundary rather than implementing separate camera systems.

## Selection States

### No selection

When no station or signal path is selected, the information region presents
general globe or summary information.

```text
┌───────────────────────┐
│ Information           │
│                       │
│ Summary               │
│ ───────────────────── │
│ Current globe state   │
│ and observation       │
│ information           │
└───────────────────────┘
```

### Station selected

Selecting a station produces station-specific information.

```text
┌───────────────────────┐
│ Information           │
│                       │
│ Station               │
│ ───────────────────── │
│ Callsign              │
│ Latitude              │
│ Longitude             │
└───────────────────────┘
```

### Signal path selected

Selecting a signal path produces path-specific information.

```text
┌───────────────────────┐
│ Information           │
│                       │
│ Signal Path           │
│ ───────────────────── │
│ Source                │
│ Destination           │
│ Propagation details   │
└───────────────────────┘
```

The exact information shown is determined by the corresponding React
presentation component rather than the Three.js object itself.

## Hover State

Hover is intentionally lighter-weight than selection.

```text
                 Pointer over object
                         │
                         ▼
                ┌──────────────────┐
                │ Raycast hit test │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Visual highlight │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │     Tooltip      │
                └──────────────────┘
```

Hover state remains renderer-local and does not require a Zustand state
update.

This keeps transient pointer movement out of the React state lifecycle.

## Filter Interaction

Filters are ordinary application controls outside the WebGL scene.

```text
┌───────────────────────┐
│ Filters               │
│                       │
│ Band     [ All      ▼]│
│ Mode     [ All      ▼]│
│ Region   [ All      ▼]│
│ Time     [ Current  ▼]│
│                       │
│       Reset Filters   │
└───────────────────────┘
            │
            ▼
     Application state
            │
            ▼
     Filter observations
            │
            ▼
      Updated UI/data
```

Filters are designed to be composable. For example, a band filter and mode
filter can be active simultaneously.

Reset returns the filter set to its default state.

## Layer Interaction

Layer controls are independent from observation filters.

```text
┌─────────────────────────┐
│ Layers                  │
│                         │
│ [✓] Solar Terminator    │
│ [✓] Solar Weather       │
│ [✓] Spot Density        │
│ [✓] Prediction Paths    │
│ [✓] Signal Paths        │
│ [✓] Stations            │
│ [✓] Anomalies           │
└─────────────────────────┘
             │
             ▼
      Layer preference
             │
             ▼
      LayerController
             │
             ▼
      Scene visibility
```

Turning off a layer changes visualization visibility without changing the
underlying observation-filter criteria.

## Motion Preferences

Motion preferences affect animated presentation without removing the
scientific information represented by the layers.

```text
┌─────────────────────────┐
│ Motion                  │
│                         │
│ System / User Preference│
│          │              │
└──────────┼──────────────┘
           ▼
   Resolve preference
           │
           ▼
    Globe renderer
           │
           ▼
   Animated layers
```

The operating system's reduced-motion preference and the application's
explicit motion preference are resolved before the resulting value enters the
Three.js subsystem.

## Responsive Layout

At viewport widths of `767px` and below, the desktop multi-column arrangement
changes to a single-column flow.

The functional regions remain available rather than being removed.

```text
┌─────────────────────────────┐
│           Header            │
├─────────────────────────────┤
│                             │
│      RADIO WEATHER GLOBE    │
│                             │
│        WebGL Canvas         │
│                             │
├─────────────────────────────┤
│           Sidebar           │
│                             │
│  Navigation                 │
│  Animation                  │
│  Filters                    │
│  Layers                     │
├─────────────────────────────┤
│        Information          │
├─────────────────────────────┤
│        Activity Panel       │
└─────────────────────────────┘
```
The mobile layout deliberately places the globe workspace immediately below
the header, followed by the control sidebar, information panel, and activity
panel. The page uses normal vertical flow at this breakpoint so the interface
can extend beyond the viewport and scroll when necessary.

Between 768px and 1099px, the application retains the desktop three-column
layout with narrower sidebar, information-panel, and bottom-panel dimensions.
At 1100px and above, the standard desktop dimensions are used.

## Responsive Design Principles

The responsive implementation preserves these priorities:

1. The globe remains usable at smaller viewport sizes.
2. Filters and layer controls remain available.
3. Information is not permanently overlaid across the globe.
4. The layout can scroll naturally when vertical space is constrained.
5. Controls remain ordinary HTML elements.
6. Keyboard interaction remains available.
7. Reduced-motion behavior is unchanged by viewport size.

Responsive browser testing validates layout behavior, but it should not be
treated as a substitute for physical-device GPU performance testing.

## Accessibility Layout

The interface deliberately separates semantic controls from the WebGL
visualization.

The globe is exposed as an interactive application region while filters,
toggles, information, and motion controls remain standard React/HTML UI.

Conceptually:

```text
Application
│
├── Header
│
├── Filter controls
│
├── Layer controls
│
├── Radio weather globe region
│   └── Interactive globe application
│
├── Information
│
└── Additional application information
```

This provides a semantic document structure around a visualization that would
otherwise be represented primarily by pixels in a canvas.

## Keyboard Interaction Reference

| Key | Globe behavior |
|---|---|
| Arrow keys | Rotate camera |
| `+` | Zoom in |
| `-` | Zoom out |
| `Enter` | Select object at viewport center |
| `Escape` | Clear current selection |

Keyboard commands are scoped to the focused globe so the application does not
capture these keys unnecessarily elsewhere on the page.

Camera reset is also exposed through the UI.

## Visual Feedback

Phase 2 uses visual changes to communicate data and interaction state.

| Visual behavior | Meaning |
|---|---|
| Object highlight | Hover or selection |
| Tooltip | Hovered-object information |
| Signal brightness | Propagation strength |
| Density pulse | Observation density |
| Prediction dissolve | Opening/closing state |
| Terminator sweep | Changing solar illumination |
| Anomaly flare | Anomaly severity |

Animation semantics are documented in
[`Animation_Specification.md`](./Animation_Specification.md).

## UX Boundaries

The following responsibilities remain deliberately separated:

- filters change the data being considered
- layers change which visual systems are visible
- camera controls change the user's viewpoint
- hover provides transient renderer-local information
- selection creates application-visible contextual state
- motion preferences change presentation behavior
- information panels present domain objects without manipulating the scene

This separation keeps individual controls predictable and prevents one UI
operation from silently changing unrelated globe state.

## Future UI Evolution

Future phases may change visual styling, panel placement, or responsive
behavior without changing the underlying rendering architecture.

When modifying the interface:

- preserve keyboard access to globe operations
- preserve semantic HTML controls outside the canvas
- avoid obscuring important globe interaction regions with permanent overlays
- keep filter and layer concepts distinct
- preserve selection synchronization with the information panel
- validate responsive behavior after layout changes
- update this document when the functional layout materially changes

## Related Documentation

- [`../architecture/Globe_Architecture.md`](../architecture/Globe_Architecture.md)
- [`../architecture/Component_Diagrams.md`](../architecture/Component_Diagrams.md)
- [`../architecture/Sequence_Diagrams.md`](../architecture/Sequence_Diagrams.md)
- [`../architecture/Layer_Architecture.md`](../architecture/Layer_Architecture.md)
- [`Animation_Specification.md`](./Animation_Specification.md)
