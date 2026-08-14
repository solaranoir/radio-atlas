# SolaraSphere: Radio Atlas

# Coding Standards

**Version:** 1.0

**Last Updated:** August 2026

---

# 1. Engineering Principles

All code should optimize for:

- Clarity over cleverness
- Small, composable units
- Explicit data flow
- Strong typing
- Predictable failure modes
- Testability
- Observability
- Accessibility
- Provider independence
- Minimal hidden state

A reviewer should be able to open an unfamiliar module and understand what it does without significant investigation.

Prefer the following workflow:

```text
Observation
    ↓
Normalization
    ↓
Domain Model
    ↓
Analysis
    ↓
Presentation
```

Avoid blending:

- Data ingestion
- Business logic
- Visualization
- AI interpretation

into the same layer.

---

# 2. Repository Structure

The project shall use a monorepo with clearly defined boundaries.

```text
radio-atlas/

├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── globe/
│   │   ├── forecast/
│   │   ├── replay/
│   │   ├── qso-story/
│   │   ├── anomalies/
│   │   ├── contacts/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── utilities/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── domain/
│   │   ├── ingestion/
│   │   ├── providers/
│   │   ├── observations/
│   │   ├── forecasting/
│   │   ├── replay/
│   │   ├── anomalies/
│   │   ├── ai/
│   │   ├── evidence/
│   │   ├── repositories/
│   │   └── models/
│
├── tests/
├── docs/
│   ├── adr/
│   ├── architecture/
│   ├── api/
│   └── testing/
│
├── scripts/
├── .github/
└── docker/
```

Feature-specific code should remain with its feature whenever possible.

---

# 3. Python Standards

## 3.1 Language Version

Use:

```text
Python 3.12+
```

Pin the version in:

- `.python-version`
- `pyproject.toml`
- `Dockerfile`
- CI configuration

---

## 3.2 Required Tooling

| Tool | Standard |
| --- | --- |
| Formatting | Ruff |
| Linting | Ruff |
| Type checking | mypy or Pyright |
| Testing | pytest |
| Dependency management | uv or Poetry |

Configuration should primarily reside in:

```text
pyproject.toml
```

---

## 3.3 Type Hints

All public functions shall be fully typed.

Preferred:

```python
def calculate_distance(
    source: GridSquare,
    destination: GridSquare,
) -> DistanceMiles:
    ...
```

Avoid:

```python
def calculate_distance(a, b):
    ...
```

---

## 3.4 Function Design

Functions should:

- Perform one conceptual operation
- Avoid mutating arguments
- Return explicit values
- Avoid hidden I/O
- Be easy to unit test

Prefer:

```python
normalized = normalize_psk_reporter_spot(raw_spot)
```

Avoid:

```python
processor.process(raw_spot)
```

when the method hides multiple responsibilities.

---

# 4. Data Modeling Standards

Use Pydantic models for:

- API input
- API output
- External provider normalization
- Configuration

Use SQLAlchemy models for persistence.

Do not use database models as API response objects.

Separate models into distinct layers:

```text
External DTO
     ↓
Normalized Domain Model
     ↓
Persistence Model
     ↓
API Response Model
```

---

# 5. TypeScript Standards

## 5.1 Required Tooling

| Tool | Standard |
| --- | --- |
| Language | TypeScript |
| Linting | ESLint |
| Formatting | Prettier |
| Component testing | React Testing Library |
| End-to-end testing | Playwright |

---

## 5.2 Strict TypeScript

Enable strict mode.

Example:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true
  }
}
```

Avoid `any`.

---

# 6. React Standards

Use:

- Functional components
- Hooks
- Composition
- Feature-based organization

Avoid oversized components.

Prefer:

```text
RadioWeatherGlobe
├── GlobeRenderer
├── SignalPathLayer
├── SpotDensityLayer
├── TerminatorLayer
├── PredictionLayer
├── AnomalyLayer
└── GlobeControls
```

---

# 7. State Management Standards

Use local state whenever possible.

Use Zustand for shared application state.

Examples:

```text
useGlobeStore
useReplayStore
useForecastStore
useUserPreferencesStore
```

Avoid a single global application store.

---

# 8. Naming Standards

Use names that reflect domain meaning.

Good examples:

```text
PropagationObservation
SignalPath
SolarConditions
ForecastWindow
ReplayFrame
QSOEvidence
PropagationAnomaly
```

Avoid generic names such as:

```text
Data
Item
Result
Info
Record
Thing
```

---

# 9. Boolean Naming Standards

Use:

```text
isLive
isSelected
hasForecast
canReplay
shouldAnimate
```

Avoid:

```text
selectedFlag
forecastBoolean
```

---

# 10. API Standards

Use RESTful endpoints.

Examples:

```text
GET  /api/v1/observations
GET  /api/v1/solar-conditions
GET  /api/v1/forecasts
GET  /api/v1/anomalies
GET  /api/v1/replay
POST /api/v1/qso-stories
```

Version APIs from the beginning.

Always use:

```text
/api/v1/
```

---

# 11. API Response Standards

Responses should follow a consistent structure.

Success:

```json
{
  "data": {
    "band": "20m",
    "probability": 0.87
  },
  "meta": {
    "provider": "observed-trend",
    "generated_at": "2026-08-14T19:42:00Z"
  }
}
```

Errors:

```json
{
  "error": {
    "code": "FORECAST_PROVIDER_UNAVAILABLE",
    "message": "Forecast data is temporarily unavailable."
  }
}
```

---

# 12. Provider Standards

External systems shall be isolated behind adapters.

Example:

```python
class SolarWeatherProvider(Protocol):
    async def current_conditions(self) -> SolarConditions:
        ...
```

Examples:

```text
NOAASolarWeatherProvider
MockSolarWeatherProvider
CachedSolarWeatherProvider
```

This approach shall also apply to:

- PSK Reporter
- QRZ
- VOACAP
- WSPR
- Reverse Beacon Network
- AI providers

---

# 13. Domain Logic Standards

Domain calculations shall remain independent of:

- FastAPI
- React
- SQLAlchemy
- HTTP clients
- OpenAI
- Redis

Prefer pure functions.

Example:

```python
detect_propagation_anomaly(observations, baseline)
```

---

# 14. Data Provenance Standards

The distinction between observed, modeled, and interpreted data shall exist in code.

Example:

```typescript
type DataProvenance =
  | "observed"
  | "modeled"
  | "interpreted";
```

Every data object shall retain information about its origin.

---

# 15. AI Engineering Standards

AI output shall never directly modify authoritative data.

Required workflow:

```text
Evidence
    ↓
Context Builder
    ↓
Prompt
    ↓
LLM
    ↓
Validation
    ↓
Labeled Interpretation
```

AI shall never:

- Invent observations
- Override measured values
- Modify contact records
- Determine whether events actually occurred

---

# 16. Prompt Engineering Standards

Prompt templates shall live outside application logic.

Example:

```text
backend/app/ai/prompts/

├── qso_story_v1.txt
├── educational_assistant_v1.txt
├── replay_caption_v1.txt
└── anomaly_explanation_v1.txt
```

Every prompt shall include:

- Version
- Purpose
- Expected inputs
- Expected outputs
- Evaluation scenarios

---

# 17. Error Handling Standards

Never silently suppress errors.

Avoid:

```python
try:
    fetch_data()
except Exception:
    pass
```

Prefer:

```python
try:
    fetch_data()
except ProviderTimeoutError as exc:
    logger.warning(
        "PSK Reporter request timed out"
    )
    raise ObservationProviderUnavailable() from exc
```

The application shall degrade gracefully.

---

# 18. Logging Standards

Use structured logging.

Every significant log entry should include:

```text
provider
request_id
band
mode
timestamp
operation
duration_ms
```

Never log:

- Passwords
- API keys
- Authentication tokens
- Sensitive user data

---

# 19. Testing Standards

Required testing layers:

```text
Unit Tests
    ↓
Integration Tests
    ↓
End-to-End Tests
    ↓
Visual Regression Tests
```

Coverage targets:

| Area | Target |
| --- | --- |
| Overall | 80% |
| Domain logic | 90%+ |
| Forecasting | 90%+ |
| Anomaly detection | 90%+ |

Coverage should measure meaningful behavior rather than satisfy arbitrary metrics.

---

# 20. Visualization Standards

Animations shall communicate data.

| Motion | Meaning |
| --- | --- |
| Pulse | Spot density |
| Brightness | Signal strength |
| Dashed line | Forecast |
| Flare | Anomaly |
| Morphing | Temporal change |

Avoid decorative animation.

Every animation should answer:

> What information does this movement communicate?

---

# 21. Accessibility Standards

Every component shall support:

- Semantic HTML
- Keyboard navigation
- Visible focus states
- Reduced motion
- Text alternatives
- Sufficient contrast

Visualization components should provide textual summaries whenever possible.

---

# 22. CSS and Styling Standards

Use Tailwind consistently.

Prefer reusable design primitives:

```text
Card
Panel
Badge
Metric
LayerToggle
StatusIndicator
```

Avoid duplicate styling patterns.

---

# 23. Commenting Standards

Comments should explain **why**, not **what**.

Avoid:

```python
# Increment count
count += 1
```

Prefer:

```python
# Ignore duplicate reports during burst intervals
# to prevent artificially inflating spot density.
```

---

# 24. Documentation Standards

Every major module shall document:

- Purpose
- Inputs
- Outputs
- Dependencies
- Failure behavior

Important architectural decisions shall receive an ADR.

Example:

```text
ADR-004: AI Evidence-Grounding Strategy
```

---

# 25. Git Standards

Use Conventional Commits.

Examples:

```text
feat(globe): add spot-density visualization
fix(replay): synchronize terminator with timeline
test(ai): add QSO Story hallucination tests
docs(adr): document forecast provider abstraction
```

---

# 26. Pull Request Standards

Every pull request shall include:

- Summary
- Rationale
- Testing performed
- Screenshots for UI changes
- Accessibility considerations
- Architecture implications
- Known limitations

---

# 27. Definition of Done

A feature is considered complete only when:

- Implementation is complete
- Types pass
- Linting passes
- Unit tests pass
- Integration tests pass
- End-to-end tests pass
- Accessibility has been verified
- Loading states exist
- Error states exist
- Logging has been implemented
- Documentation has been updated
- Architecture diagrams have been updated
- CI passes
- Code review has been completed

---

# 28. AI-Assisted Development Standard

AI may accelerate implementation, but the repository shall never contain code the developer cannot explain, test, or maintain.

For significant AI-assisted changes:

1. Review the implementation.
2. Simplify unnecessary abstractions.
3. Add or update tests.
4. Verify security assumptions.
5. Review performance implications.
6. Verify architectural consistency.
7. Document significant decisions.

---

# 29. Recommended Tooling

| Area | Standard |
| --- | --- |
| Python formatting | Ruff |
| Python type checking | mypy or Pyright |
| Python testing | pytest |
| TypeScript linting | ESLint |
| TypeScript formatting | Prettier |
| Component testing | React Testing Library |
| End-to-end testing | Playwright |
| API contracts | OpenAPI |
| Commit format | Conventional Commits |
| CI | GitHub Actions |
| Architecture decisions | ADRs |
| Dependency management | uv or Poetry |
| Security scanning | CodeQL |
