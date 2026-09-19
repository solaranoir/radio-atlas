# Phase 2 Review Notes

## Purpose

This document records the disposition of architectural and implementation
concerns identified during a review of the Phase 2 Radio Weather Globe.

The review occurred before completion of the Phase 2 architecture
documentation. Some findings identified genuine integration gaps, some were
documentation gaps that have since been resolved, and others describe work
that is intentionally scheduled for later phases.

This document does not redefine the Phase 2 roadmap. It records known
limitations and identifies the phase in which deferred work is expected to be
addressed.

## Review Summary

The review found that the major Phase 2 visualization, interaction, layer,
state, animation, accessibility, and testing subsystems were implemented, but
identified several places where the implemented feature surface was ahead of
its production data integration.

Story 12.5 resolved the Phase 2 live-observation integration gap. Filtered
observations now drive the globe's station markers, signal arcs, and
spot-density visualization through the React-to-renderer boundary, and the
production rendering context no longer creates representative observation
fixtures for those layers.

The current architecture should therefore be understood as a completed globe
visualization and interaction foundation with live observation rendering in
place. Data capabilities intentionally assigned to later phases, including
historical replay and prediction-path population, remain deferred according to
the roadmap.

## Live Observation Integration

### Finding

The Phase 2 review identified that the React application retrieved and
filtered observation data while the Three.js rendering context still
initialized signal arcs, stations, and spot-density visualization from
representative data created by the rendering context.

### Disposition

**Resolved in Story 12.5.**

Filtered observations now cross the existing React-to-renderer boundary as
observation-derived visualization models. The application adapts filtered
observations into signal paths, station markers, and spot-density regions and
supplies those models to `GlobeRenderingContext`.

`GlobeRenderingContext` no longer creates representative observation fixtures
for signal arcs, stations, or spot density. It remains independent of API
retrieval and receives renderer-ready visualization data through
`setObservationVisualization()`.

Station markers are reconciled through `StationCollection`, while the existing
signal-arc and spot-density layer reconciliation APIs receive their
observation-derived models through the same renderer update.

Automated coverage includes observation-to-visualization adapter tests,
station reconciliation tests, a React-to-Three.js integration-seam test, and
browser tests using deterministic API-backed observations.

### Later-phase relationship

Phase 3 can reuse this renderer boundary for time-windowed historical playback
frames without coupling `GlobeRenderingContext` directly to an API client.

Current live observations and future replay-derived visualization data can
therefore share the same rendering architecture.

## Filtering and Globe Synchronization

### Finding

The Phase 2 review identified that band, mode, region, and time filtering
operated on application observation data without altering the corresponding
rendered observation-derived globe objects.

### Disposition

**Resolved in Story 12.5.**

The visualization adapter now consumes the filtered observation collection, so
filter changes update the station, signal-path, and spot-density models
supplied to the existing Three.js rendering context.

End-to-end coverage verifies this behavior with an observation-backed station:
the station is rendered and selectable while its observation satisfies the
active filters and is removed from the rendered scene when a subsequent
filter excludes that observation.

Visual regression tests now use deterministic mocked observation API data
rather than relying on production renderer fixtures. Their baselines therefore
represent the live observation rendering path introduced by Story 12.5.

## Prediction Paths

### Finding

`PredictionPathLayer` and the rendering-context prediction-path API exist, but
Phase 2 does not yet have a production forecast source that supplies prediction
paths.

### Disposition

**Visualization capability implemented; production data source intentionally
deferred.**

The Phase 2 layer establishes the rendering contract and visual semantics for
prediction paths. It should not be described as a functioning production
forecast pipeline.

### Planned work

Phase 4 implements the actual forecasting system, including:

- a forecast abstraction
- a baseline statistical forecaster
- confidence scoring
- forecast APIs
- forecast visualization
- forecast overlays integrated with the Radio Weather Globe

Phase 2 therefore provides the visualization primitive that Phase 4 can
populate with real forecast results.

## Propagation-Strength Animation

### Finding

The Phase 2 review identified that signal-path animation and brightness
behavior were implemented while the rendered paths still used representative
strength values rather than strength derived from live observations.

### Disposition

**Resolved in Story 12.5.**

Observation-backed signal paths now derive their normalized strength from the
observation's `snr_db` value before crossing the renderer boundary.

The visualization adapter maps SNR values linearly from -30 dB through +10 dB
onto the renderer's 0 through 1 strength range, clamps values outside that
range, and assigns zero strength when SNR is unavailable.

The existing signal-path rendering and animation behavior therefore consumes
observation-derived strength without requiring a redesign of the animation
mechanism.

## End-to-End Test Coverage

### Finding

The Phase 2 review originally identified that E2E coverage validated layer
visibility persistence, filter behavior, station selection, and camera
rotation/reset, but did not verify that filtering changed observation-backed
objects rendered in the Three.js scene.

### Disposition

**Resolved in Story 12.5.**

The E2E observation fixture now supplies deterministic API-backed radio
observations to the production application path.

Filter coverage verifies both application state and rendered behavior. An
observation-backed station is selectable while its observation satisfies the
active filters and is no longer selectable after a subsequent filter excludes
that observation.

Separate E2E coverage continues to validate layer visibility persistence,
station selection and clearing, and camera rotation/reset.

Phase 3 can extend this integration-testing pattern for replay-to-globe
synchronization.

Phase 5 remains responsible for expanded CI coverage gates and the complete
release-candidate regression suite.

## Coverage Scope

### Finding

The reported unit-test coverage percentage does not represent every
integration and rendering-wiring file equally. Several lifecycle, hook, API,
and rendering-boundary files are not included in the measured unit-test
surface.

### Disposition

**Known testing limitation.**

The percentage should be interpreted as coverage of the configured unit-test
surface rather than proof that every application integration path has been
exercised.

Phase 2 supplements unit testing with visual-regression and E2E suites.

Future coverage expansion should prioritize integration boundaries rather than
optimizing solely for a higher aggregate percentage.

Phase 5 CI hardening explicitly includes expanded test-coverage gates, and the
release-readiness work requires a comprehensive test report and full
regression run.

## Visual Regression Baseline Validation

### Finding

During Phase 2 closeout validation, the deterministic Playwright visual
regression tests for the base globe, signal paths, and spot-density overlay
each differed from their existing baselines by exactly 26 pixels.

The result was reproduced across two consecutive test runs. Inspection of the
base-globe diff showed that the changed pixels were confined to very small
Earth-surface fragments near southern South America rather than changes to
camera position, globe geometry, markers, layer composition, or overall
rendering structure.

The full-motion animation test continued to pass.

No frontend source files or visual-regression baseline files were modified by
Story 12.4.

### Disposition

**Stable visual-baseline discrepancy; baseline update intentionally deferred.**

Because Story 12.4 is documentation-only and did not modify frontend rendering
code, the existing screenshots were not regenerated merely to make the
validation suite pass.

The discrepancy should be investigated or deliberately re-baselined in a
frontend-focused change where the rendering environment and resulting
screenshots can be reviewed independently.

Until then, Phase 2 closeout should report the visual-regression suite as
1 of 4 tests passing, with three deterministic tests failing on the documented
26-pixel baseline difference rather than reporting the visual suite as fully
passing.

## Animation Semantics Registry

### Finding

`ANIMATION_SEMANTICS` centralizes the documented meaning of animation types,
but the registry itself is not intended to function as the runtime dispatcher
for every animation.

### Disposition

**Documentation and semantic contract, not runtime dependency injection.**

Individual rendering layers implement the corresponding visual behaviors.
The registry establishes a shared vocabulary and prevents animation meanings
from drifting as new visualization features are added.

Future layers should preserve those semantics even when their implementation
does not directly import the registry.

## Solar Terminator Sweep

### Finding

The solar terminator is recalculated periodically rather than animated as a
continuous decorative rotation.

### Disposition

**Intentional implementation choice.**

The terminator represents changing solar illumination rather than arbitrary
continuous movement.

Its update behavior favors scientifically meaningful state over unnecessary
per-frame computation. The semantic term "sweep" describes the changing
day/night boundary over time, not a requirement that the boundary move every
animation frame.

## Performance Evidence

### Finding

Phase 2 includes runtime performance instrumentation and development profiling,
but does not contain a formal hardware benchmark report proving the desktop
and mobile targets across representative devices.

### Disposition

**Development target observed; production performance certification deferred.**

Desktop development profiling observed approximately 60 FPS.

Responsive browser profiling also remained approximately 60 FPS, but browser
responsive emulation is not equivalent to physical mobile hardware and is not
presented as such.

Phase 5 explicitly includes:

- frontend performance profiling
- globe and chart rendering profiling
- bundle-size optimization
- rendering optimization
- performance benchmarks
- before-and-after performance comparison
- final accessibility and performance sign-off

Formal release-level performance evidence therefore belongs to Phase 5.

## Deck.gl

### Finding

The original architecture selected Three.js for globe rendering and Deck.gl
for overlays, while the implemented Phase 2 globe uses Three.js for both.

### Disposition

**Resolved architectural deviation.**

ADR-010, "Standardize Globe Overlays on Three.js," records the implemented
decision and supersedes only the Deck.gl overlay portion of ADR-001.

Deck.gl is not required merely to satisfy the original implementation plan.

The decision can be revisited if later data volume or geospatial requirements
demonstrate a measurable need for another rendering engine.

Phase 5 performance work should interpret references to optimizing "Three.js
and Deck.gl rendering paths" according to the rendering engines actually in
use at that time.

## Architecture Documentation

### Finding

The review found that the required Phase 2 architecture documents and
wireframes were absent.

### Disposition

**Resolved in Story 12.4.**

Phase 2 now includes:

- `docs/architecture/Globe_Architecture.md`
- `docs/architecture/Component_Diagrams.md`
- `docs/architecture/Sequence_Diagrams.md`
- `docs/architecture/Layer_Architecture.md`
- `docs/ux/Wireframes.md`
- `docs/ux/Animation_Specification.md`

ADR-010 additionally records the rendering-engine decision discovered during
the documentation review.

## Earth Texture Assets

### Finding

The globe uses a day Earth texture rather than separate day, night, normal,
and specular texture maps.

Day/night state is communicated through lighting and the solar-terminator
visualization.

### Disposition

**Not considered a Phase 2 architectural blocker.**

The Phase 2 requirement is to communicate radio-weather and solar context on
the globe. The current lighting and terminator system provides that semantic
information without requiring a particular number of texture maps.

Additional Earth material assets can be introduced later if they provide a
measurable visual or performance benefit.

## Repository Hygiene

### Finding

The reviewed archive contained environment, cache, build, coverage, and
platform-generated files.

### Disposition

**Requires repository-specific verification.**

An exported or zipped working directory is not sufficient evidence that every
contained file is tracked by Git.

Before Phase 2 closeout, repository status should be checked to distinguish
tracked source files from ignored local artifacts.

Production configuration, secrets handling, container packaging, and
environment management are explicitly revisited during Phase 5
productionization.

A real `.env` containing secrets must not be committed. Environment templates
should contain placeholders rather than credentials.

## Relationship to Later Phases

Phase 2 establishes the interactive visualization platform.

Phase 3 builds analytics and historical replay on that platform. In
particular, it introduces time-windowed observation retrieval and explicitly
integrates playback frames with the existing globe renderer.

Phase 4 builds the production forecasting system. The prediction-path
visualization established in Phase 2 provides a rendering target for those
forecast results.

Phase 5 converts the completed application into a release candidate. It
contains the broader performance profiling, optimization, accessibility
verification, CI coverage expansion, full regression testing, configuration
hardening, and production-readiness work that should not be retroactively
pulled into Phase 2.

## Phase 2 Closeout Interpretation

The review identified an important distinction between **visualization
capability** and **production data integration**.

The Phase 2 globe architecture, rendering layers, interaction system, layer
management, UI, animation semantics, accessibility features, and testing
infrastructure establish the visualization platform required by later phases.

Story 12.5 completed the production observation-data integration for the
Phase 2 globe. Live filtered observations now drive signal arcs, station
markers, and spot-density visualization, and filter changes propagate to
those rendered objects.

Phase 2 documentation should still not claim that:

- production forecasts currently populate prediction paths
- physical mobile-device performance has been formally certified

Those remaining limitations are recorded explicitly so subsequent phases can
extend the existing architecture without relying on assumptions that the
current code does not satisfy.
