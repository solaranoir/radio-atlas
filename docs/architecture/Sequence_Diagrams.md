# Radio Weather Globe Sequence Diagrams

## Purpose

This document describes the major runtime interactions within the Radio Weather
Globe.

The diagrams focus on boundaries where control or data moves between React,
Zustand application state, the Three.js rendering subsystem, visualization
layers, and user interaction.

For the overall system structure, see
[`Globe_Architecture.md`](./Globe_Architecture.md).

## Globe Initialization

The React application owns creation and destruction of the imperative Three.js
rendering context through `useGlobeRenderer`.

```mermaid
sequenceDiagram
    participant React as GlobeRenderer
    participant Hook as useGlobeRenderer
    participant Context as GlobeRenderingContext
    participant Renderer as Three.js Renderer
    participant Layers as Visualization Layers
    participant Browser

    React->>Hook: Mount with container and application state
    Hook->>Context: new GlobeRenderingContext()
    Context->>Renderer: Create renderer, scene, camera, controls
    Context->>Layers: Create visualization layers
    Context->>Renderer: Register pointer listeners

    Hook->>Context: setSelectionChangeHandler()
    Hook->>Context: Restore layer visibility
    Hook->>Context: mount(container)
    Context->>Browser: Append WebGL canvas
    Context->>Browser: Append tooltip element
    Context->>Context: resize(width, height)

    Hook->>Context: start()
    Context->>Browser: requestAnimationFrame(render)

    Hook->>Browser: Observe container size
```

The rendering context owns one Three.js renderer and one animation loop for the
mounted globe.

## Globe Disposal

React also owns the lifetime boundary for renderer cleanup.

```mermaid
sequenceDiagram
    participant React as GlobeRenderer
    participant Hook as useGlobeRenderer
    participant Observer as ResizeObserver
    participant Context as GlobeRenderingContext
    participant Layers as Visualization Layers
    participant Renderer as Three.js Renderer

    React->>Hook: Unmount
    Hook->>Observer: disconnect()
    Hook->>Context: dispose()

    Context->>Context: Stop clock and animation loop
    Context->>Context: Clear hover and tooltip
    Context->>Layers: dispose()
    Context->>Context: Dispose navigation controls
    Context->>Context: Remove pointer listeners
    Context->>Renderer: Remove canvas
    Context->>Renderer: dispose()

    Hook->>Hook: Clear rendering-context reference
```

Explicit disposal prevents stale canvases, event listeners, animation loops,
and GPU resources from surviving a React unmount.

## Render Loop

All animated globe layers advance through the central rendering loop.

```mermaid
sequenceDiagram
    participant Browser
    participant Context as GlobeRenderingContext
    participant Clock
    participant Layers as Animated Layers
    participant Solar as Solar Systems
    participant Controls
    participant Renderer
    participant Monitor as RenderingPerformanceMonitor

    Browser->>Context: animation frame
    Context->>Clock: getDelta()
    Clock-->>Context: deltaSeconds

    Context->>Layers: Update signal arcs
    Context->>Layers: Update spot density
    Context->>Layers: Update prediction paths

    alt Solar update interval reached
        Context->>Solar: Update terminator
        Context->>Solar: Update solar lighting
    end

    Context->>Layers: Update anomalies
    Context->>Controls: update()
    Context->>Renderer: render(scene, camera)

    Context->>Monitor: update(deltaSeconds)

    opt Performance sample available
        Monitor-->>Context: Performance snapshot
        Context-->>React: Performance callback
    end

    Context->>Browser: requestAnimationFrame(render)
```

There is no independent animation loop for individual visualization layers.

## Observation Retrieval and Filtering

Observation retrieval and filtering remain outside the Three.js rendering
classes.

```mermaid
sequenceDiagram
    participant API as Radio Atlas API
    participant Hook as useObservations
    participant React as React Application
    participant Filters as Filter Logic
    participant Store as Zustand
    participant UI as Globe UI

    Hook->>API: Request observations
    API-->>Hook: Radio observations
    Hook-->>React: Observation data

    Store-->>React: Current filter state
    React->>Filters: filterObservations(observations, filters)
    Filters-->>React: Filtered observations

    React-->>UI: Render filtered counts and controls
```

Filter calculations are pure application logic. They can therefore be tested
without a Three.js scene or browser WebGL context.

## Filter Interaction

When the user changes a filter, `FilterPanel` reports the change to
`GlobeRenderer`, which updates the filter state in Zustand. The updated state
then drives application-level observation filtering.

```mermaid
sequenceDiagram
    participant User
    participant Panel as FilterPanel
    participant React as GlobeRenderer
    participant Store as Zustand
    participant Filters as Filter Logic
    participant UI as React UI

    User->>Panel: Change band, mode, region, or time
    Panel->>React: onChange(updated filters)
    React->>Store: Update filter state
    Store-->>React: Updated filter state
    React->>Filters: Apply current filters
    Filters-->>React: Matching observations
    React-->>UI: Updated activity counts and derived data
    UI-->>User: Updated observation information
```
In the current Phase 2 implementation, this sequence does not continue from
the filtered observation collection into the Three.js station, signal-path, or
spot-density layers. Filter changes therefore update application-level
observation information but do not yet alter those rendered observation
layers.

Resetting the filters follows the same state-update path, with the store
returning filter values to their defaults.

## Layer Visibility

Layer controls do not manipulate Three.js scene objects directly.

```mermaid
sequenceDiagram
    participant User
    participant Controls as LayerControls
    participant Preferences as Layer Preferences
    participant React as GlobeRenderer
    participant Hook as useGlobeRenderer
    participant Context as GlobeRenderingContext
    participant Controller as LayerController
    participant Scene as Three.js Scene

    User->>Controls: Toggle layer
    Controls->>Preferences: Persist visibility preference
    Controls->>React: Visibility changed
    React->>Hook: setLayerVisible(id, visible)
    Hook->>Context: setLayerVisible(id, visible)

    alt Enable layer
        Context->>Controller: enable(id)
    else Disable layer
        Context->>Controller: disable(id)
    end

    Context->>Scene: Apply layer visibility
```

Persisted preferences allow layer choices to survive an application reload.

## Pointer Hover

Hover interaction is renderer-owned because it depends on the Three.js scene
and raycasting.

```mermaid
sequenceDiagram
    participant User
    participant Canvas
    participant Context as GlobeRenderingContext
    participant Raycaster
    participant Scene
    participant Tooltip

    User->>Canvas: Move pointer
    Canvas->>Context: pointermove
    Context->>Raycaster: Convert pointer and cast ray
    Raycaster->>Scene: Intersect visible objects
    Scene-->>Raycaster: Intersections
    Raycaster-->>Context: Hover target

    alt Hover target found
        Context->>Context: Apply hover highlight
        Context->>Tooltip: Build and show tooltip
        Tooltip-->>User: Object information
    else No target
        Context->>Context: Clear hover state
        Context->>Tooltip: Hide tooltip
    end
```

Hover state remains inside the renderer because it is transient presentation
state and does not need to drive React application state.

## Pointer Selection

Selection crosses the renderer/application boundary because selected-object
details are displayed by React.

```mermaid
sequenceDiagram
    participant User
    participant Canvas
    participant Context as GlobeRenderingContext
    participant Raycaster
    participant React as GlobeRenderer
    participant Store as Zustand
    participant Panel as InformationPanel

    User->>Canvas: Pointer down
    Canvas->>Context: Record pointer position

    User->>Canvas: Pointer up
    Canvas->>Context: Evaluate click gesture

    alt Gesture is a click
        Context->>Raycaster: Raycast scene
        Raycaster-->>Context: Selectable object

        alt Object found
            Context->>Context: Highlight selected object
            Context-->>React: onSelectionChange(selection)
            React->>Store: setSelection(selection)
            Store-->>Panel: Updated selection
            Panel-->>User: Display object details

            Store-->>React: Selection state
            React->>Context: setSelection(selection)
            Context->>Context: Detect same selection
        else No selectable object
            Context->>Context: Clear selection
        end
    end
```

The renderer recognizes an already-selected object when React synchronizes the
same selection back into the context. This prevents redundant selection work
and callback recursion.

## Selection Initialization

Selection callbacks must be installed after the rendering context exists.

```mermaid
sequenceDiagram
    participant React
    participant Hook as useGlobeRenderer
    participant Ref as renderingContextRef
    participant Context as GlobeRenderingContext

    React->>Hook: Mount
    Hook->>Context: new GlobeRenderingContext()
    Hook->>Ref: Store context reference
    Hook->>Context: setSelectionChangeHandler(callback)
    Hook->>Context: mount()
    Hook->>Context: start()

    Note over Hook,Context: Initial callback registration occurs after context creation.

    React->>Hook: Callback identity changes
    Hook->>Ref: Read existing context
    Ref-->>Hook: Context
    Hook->>Context: setSelectionChangeHandler(updated callback)
```

This ordering is important. Registering the initial callback only in an effect
that executes before the context exists leaves the Three.js renderer without a
selection callback until that callback later changes.

The Phase 2 end-to-end selection test protects this integration boundary.

## Keyboard Globe Navigation

Keyboard input is scoped to the focused globe application rather than being
registered as an unrestricted global shortcut.

```mermaid
sequenceDiagram
    participant User
    participant Globe as GlobeRenderer
    participant Hook as useGlobeRenderer
    participant Context as GlobeRenderingContext
    participant Camera
    participant Controls

    User->>Globe: Focus globe
    User->>Globe: Press navigation key

    alt Arrow key
        Globe->>Hook: rotateCamera()
        Hook->>Context: rotateCamera()
        Context->>Camera: Update spherical position
        Context->>Controls: update()
    else Plus or minus
        Globe->>Hook: zoomCamera()
        Hook->>Context: zoomCamera()
        Context->>Camera: Update distance
        Context->>Controls: update()
    else Enter
        Globe->>Hook: selectAtViewportCenter()
        Hook->>Context: selectAtViewportCenter()
        Context->>Context: Raycast center
    else Escape
        Globe->>Hook: clearCurrentSelection()
        Hook->>Context: clearCurrentSelection()
    end
```

The camera is manipulated through the rendering context rather than directly
from React.

## Camera Reset

Camera reset delegates to the existing navigation-control state.

```mermaid
sequenceDiagram
    participant User
    participant UI as Globe UI
    participant Hook as useGlobeRenderer
    participant Context as GlobeRenderingContext
    participant Controls as Navigation Controls

    User->>UI: Activate Reset Camera
    UI->>Hook: resetCamera()
    Hook->>Context: resetCamera()
    Context->>Controls: reset()
    Context->>Controls: update()
```

The Phase 2 end-to-end suite verifies that rotation changes the visible globe
state and that resetting the camera restores the initial selection geometry.

## Solar Weather Update

Solar-weather data enters the rendering system explicitly through the React
adapter.

```mermaid
sequenceDiagram
    participant Source as Solar Data Source
    participant Hook as useSolarWeather
    participant React
    participant RendererHook as useGlobeRenderer
    participant Context as GlobeRenderingContext
    participant Layer as SolarWeatherLayer

    Hook->>Source: Retrieve solar-weather data
    Source-->>Hook: Solar-weather snapshot
    Hook-->>React: Snapshot
    React->>RendererHook: solarWeather
    RendererHook->>Context: setSolarWeatherSnapshot(snapshot)
    Context->>Layer: setSnapshot(snapshot)
    Layer->>Layer: Update visualization resources
```

The Three.js solar-weather layer does not retrieve NOAA or API data itself.

## Anomaly Update

Anomaly detection and rendering are similarly separated.

```mermaid
sequenceDiagram
    participant Observations
    participant Detection as Anomaly Logic
    participant Hook as useAnomalies
    participant React
    participant RendererHook as useGlobeRenderer
    participant Context as GlobeRenderingContext
    participant Layer as AnomalyLayer

    Observations->>Detection: Observation data
    Detection-->>Hook: Detected anomalies
    Hook-->>React: Anomalies
    React->>RendererHook: anomalies
    RendererHook->>Context: setAnomalies(anomalies)
    Context->>Layer: setAnomalies(anomalies)
```

Detection remains testable independently from Three.js rendering.

## Reduced-Motion Flow

Accessibility preferences are resolved outside visualization layers.

```mermaid
sequenceDiagram
    participant OS as Operating System
    participant Hook as useReducedMotionPreference
    participant Control as MotionPreferenceControl
    participant React
    participant RendererHook as useGlobeRenderer
    participant Context as GlobeRenderingContext
    participant Layers as Animated Layers

    OS-->>Hook: prefers-reduced-motion
    Hook-->>React: System preference
    Control-->>React: Explicit user preference
    React->>React: Resolve effective preference
    React->>RendererHook: reducedMotion
    RendererHook->>Context: setReducedMotion(boolean)

    loop Each animation frame
        Context->>Layers: update(delta, reducedMotion)
    end
```

This design keeps accessibility policy outside individual Three.js layers while
allowing those layers to adjust their presentation.

## Performance Reporting

Performance sampling is part of the rendering loop but is not propagated to
React every frame.

```mermaid
sequenceDiagram
    participant Context as GlobeRenderingContext
    participant Renderer as Three.js Renderer
    participant Monitor as RenderingPerformanceMonitor
    participant React

    Context->>Renderer: render(scene, camera)
    Context->>Monitor: update(deltaSeconds)

    alt Sampling interval reached
        Monitor-->>Context: Performance snapshot
        Context-->>React: onPerformanceSnapshot(snapshot)
    else No sample
        Monitor-->>Context: No snapshot
    end
```

This prevents performance instrumentation itself from creating a per-frame
React update path.

## Related Documentation

- [`Globe_Architecture.md`](./Globe_Architecture.md)
- [`Component_Diagrams.md`](./Component_Diagrams.md)
- [`Layer_Architecture.md`](./Layer_Architecture.md)
- [`../ux/Animation_Specification.md`](../ux/Animation_Specification.md)
- [`../ux/Wireframes.md`](../ux/Wireframes.md)
