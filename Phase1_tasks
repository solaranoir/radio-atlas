# SolaraSphere: Radio Atlas

# Phase 1 Engineering Roadmap: Data Platform (Weeks 2--3)

**Version:** 1.0

------------------------------------------------------------------------

## Sprint Theme

*From raw radio observations to a reliable, queryable data platform.*

The objective of Phase 1 is to establish the entire data foundation for
Radio Atlas. By the end of this phase, the system should be continuously
ingesting live data, normalizing it into a unified domain model, storing
it in PostgreSQL, and exposing it through a documented API.

------------------------------------------------------------------------

## Goals

-   Implement the NOAA provider
-   Implement the PSK Reporter provider
-   Normalize observations
-   Create the PostgreSQL schema
-   Build FastAPI endpoints

------------------------------------------------------------------------

## Checkpoint

-   Live ingestion running
-   API documented

------------------------------------------------------------------------

## Documentation Requirements

-   Entity Relationship Diagram (ERD)
-   Provider contracts
-   OpenAPI documentation

------------------------------------------------------------------------

# Epic 1: Development Environment and Repository Foundation

## Story 1.1: Establish the backend project structure

### Acceptance Criteria

-   Backend repository structure is created
-   Coding standards are applied
-   Dependency management is configured

### Tasks

-   Create the `backend/` directory structure
-   Configure `pyproject.toml`
-   Configure Ruff
-   Configure mypy or Pyright
-   Configure pytest
-   Create environment configuration
-   Configure `.editorconfig`
-   Configure `.gitignore`

------------------------------------------------------------------------

## Story 1.2: Configure Docker development services

### Acceptance Criteria

-   Backend services run locally with a single command

### Tasks

-   Create `docker-compose.yml`
-   Configure the PostgreSQL container
-   Configure the Redis container
-   Configure the FastAPI container
-   Configure persistent database volumes
-   Create startup scripts
-   Document local development setup

------------------------------------------------------------------------

## Story 1.3: Configure CI

### Acceptance Criteria

-   Pull requests automatically execute tests

### Tasks

-   Create GitHub Actions workflows
-   Configure linting
-   Configure unit testing
-   Configure build validation

------------------------------------------------------------------------

# Epic 2: Observation Provider Architecture

## Story 2.1: Implement provider contracts

### Acceptance Criteria

-   All external providers implement a common interface

### Tasks

-   Implement `ObservationProvider`
-   Create provider abstractions
-   Define asynchronous provider contracts
-   Create mock providers
-   Write provider unit tests

------------------------------------------------------------------------

## Story 2.2: Document provider contracts

### Acceptance Criteria

-   Provider interfaces are documented

### Tasks

-   Create `Provider_Contracts.md`
-   Document required methods
-   Document provider responsibilities
-   Create provider sequence diagrams
-   Add architecture diagrams

------------------------------------------------------------------------

# Epic 3: NOAA Provider Implementation

## Story 3.1: Research NOAA data sources

### Acceptance Criteria

-   Required NOAA endpoints are identified

### Tasks

-   Identify NOAA APIs
-   Identify solar data feeds
-   Document refresh intervals
-   Identify rate limits
-   Document response formats

------------------------------------------------------------------------

## Story 3.2: Create NOAA data models

### Acceptance Criteria

-   NOAA responses are normalized

### Tasks

-   Create models for solar flux
-   Create models for Kp index
-   Create models for sunspot number
-   Create models for aurora data
-   Create models for geomagnetic data

------------------------------------------------------------------------

## Story 3.3: Implement NOAA ingestion

### Acceptance Criteria

-   Solar data is successfully ingested

### Tasks

-   Create `NOAAProvider`
-   Implement HTTP requests
-   Implement retry logic
-   Implement timeout handling
-   Implement response validation
-   Implement structured logging

------------------------------------------------------------------------

## Story 3.4: Test the NOAA provider

### Acceptance Criteria

-   All NOAA tests pass

### Tasks

-   Write unit tests
-   Write integration tests
-   Test malformed responses
-   Test timeout handling
-   Test retry behavior

------------------------------------------------------------------------

# Epic 4: PSK Reporter Provider Implementation

## Story 4.1: Research PSK Reporter data sources

### Acceptance Criteria

-   Data retrieval strategy is documented

### Tasks

-   Research PSK Reporter endpoints
-   Identify data formats
-   Document query parameters
-   Identify update frequency
-   Identify request limitations

------------------------------------------------------------------------

## Story 4.2: Create PSK Reporter data models

### Acceptance Criteria

-   Spot data is normalized

### Tasks

-   Create callsign models
-   Create frequency models
-   Create band models
-   Create operating mode models
-   Create coordinate models
-   Create grid square models

------------------------------------------------------------------------

## Story 4.3: Implement PSK Reporter ingestion

### Acceptance Criteria

-   Live spots are successfully ingested

### Tasks

-   Create `PSKReporterProvider`
-   Implement API integration
-   Normalize responses
-   Implement rate limiting
-   Implement retry handling
-   Implement logging

------------------------------------------------------------------------

## Story 4.4: Test PSK Reporter integration

### Acceptance Criteria

-   Integration tests pass

### Tasks

-   Test valid responses
-   Test invalid responses
-   Test missing fields
-   Test API failures
-   Test rate limiting

------------------------------------------------------------------------

# Epic 5: Observation Normalization

## Story 5.1: Create the core observation model

### Acceptance Criteria

-   All providers map to a single domain model

### Tasks

-   Create `PropagationObservation`
-   Create `SolarObservation`
-   Create `SpotObservation`
-   Create `StationObservation`

------------------------------------------------------------------------

## Story 5.2: Implement the normalization pipeline

### Acceptance Criteria

-   External provider data is transformed into internal models

### Tasks

-   Implement validation
-   Implement transformation
-   Implement normalization
-   Implement persistence

------------------------------------------------------------------------

## Story 5.3: Add data validation

### Acceptance Criteria

-   Invalid data is rejected

### Tasks

-   Validate timestamps
-   Validate coordinates
-   Validate frequencies
-   Validate bands
-   Validate callsigns
-   Validate grid squares

------------------------------------------------------------------------

## Story 5.4: Add duplicate detection

### Acceptance Criteria

-   Duplicate observations are identified

### Tasks

-   Implement spot deduplication
-   Implement timestamp validation
-   Implement observation uniqueness rules

------------------------------------------------------------------------

# Epic 6: Database Architecture

## Story 6.1: Design the database schema

### Acceptance Criteria

-   The schema supports all Phase 1 requirements

### Tasks

-   Create `users`
-   Create `stations`
-   Create `spots`
-   Create `solar_conditions`
-   Create `providers`

------------------------------------------------------------------------

## Story 6.2: Create the Entity Relationship Diagram

### Acceptance Criteria

-   ERD is complete and documented

### Tasks

-   Document primary keys
-   Document foreign keys
-   Document relationships
-   Document indexes

------------------------------------------------------------------------

## Story 6.3: Create database migrations

### Acceptance Criteria

-   Migrations execute successfully

### Tasks

-   Configure Alembic
-   Create the initial migration
-   Create indexes
-   Create rollback procedures

------------------------------------------------------------------------

## Story 6.4: Test the database

### Acceptance Criteria

-   Database tests pass

### Tasks

-   Test inserts
-   Test updates
-   Test deletes
-   Test relationships
-   Test constraints

------------------------------------------------------------------------

# Epic 7: Ingestion Services

## Story 7.1: Implement background ingestion jobs

### Acceptance Criteria

-   Providers run automatically

### Tasks

-   Implement NOAA polling
-   Implement PSK Reporter polling

------------------------------------------------------------------------

## Story 7.2: Implement scheduling

### Acceptance Criteria

-   Providers refresh automatically

### Tasks

-   Configure NOAA polling every 5 minutes
-   Configure PSK Reporter polling every 1 minute

------------------------------------------------------------------------

## Story 7.3: Implement failure handling

### Acceptance Criteria

-   Provider failures do not stop ingestion

### Tasks

-   Implement retry logic
-   Implement circuit breakers
-   Implement error handling
-   Implement dead-letter handling

------------------------------------------------------------------------

# Epic 8: FastAPI API Development

## Story 8.1: Create API infrastructure

### Acceptance Criteria

-   FastAPI is configured

### Tasks

-   Configure routing
-   Configure middleware
-   Configure dependency injection
-   Configure exception handling

------------------------------------------------------------------------

## Story 8.2: Create the observations API

### Acceptance Criteria

-   Observation data is accessible

### Tasks

-   Implement `GET /api/v1/observations`
-   Support time filtering
-   Support pagination
-   Support band filtering

------------------------------------------------------------------------

## Story 8.3: Create the solar conditions API

### Acceptance Criteria

-   Solar data is accessible

### Tasks

-   Implement `GET /api/v1/solar-conditions`

------------------------------------------------------------------------

## Story 8.4: Create the stations API

### Acceptance Criteria

-   Station information is accessible

### Tasks

-   Implement `GET /api/v1/stations`

------------------------------------------------------------------------

## Story 8.5: Add API validation

### Acceptance Criteria

-   Invalid requests are rejected

### Tasks

-   Implement request validation
-   Implement response validation
-   Implement error handling

------------------------------------------------------------------------

# Epic 9: API Documentation

## Story 9.1: Generate OpenAPI documentation

### Acceptance Criteria

-   OpenAPI documentation is available

### Tasks

-   Document endpoints
-   Document request models
-   Document response models
-   Document error responses
-   Document example payloads

------------------------------------------------------------------------

## Story 9.2: Create API examples

### Acceptance Criteria

-   API examples are available for all endpoints

### Tasks

-   Document requests
-   Document responses
-   Document query parameters
-   Document error examples

------------------------------------------------------------------------

# Epic 10: Observability

## Story 10.1: Implement structured logging

### Acceptance Criteria

-   All providers emit structured logs

### Tasks

-   Log provider
-   Log operation
-   Log request duration
-   Log record counts
-   Log errors

------------------------------------------------------------------------

## Story 10.2: Implement health monitoring

### Acceptance Criteria

-   Provider health can be monitored

### Tasks

-   Create `GET /health`
-   Create `GET /health/noaa`
-   Create `GET /health/psk-reporter`

------------------------------------------------------------------------

# Phase 1 Definition of Done

-   NOAA provider implemented
-   PSK Reporter provider implemented
-   Provider contracts documented
-   Observations normalized
-   PostgreSQL schema implemented
-   Database migrations created
-   Background ingestion running
-   FastAPI endpoints implemented
-   OpenAPI documentation generated
-   ERD completed
-   Unit tests passing
-   Integration tests passing
-   CI pipeline passing
-   Docker environment functioning

------------------------------------------------------------------------

## Estimated Effort

-   Duration: 2 weeks (10 working days)
-   Estimated engineering effort: 80 to 120 hours

------------------------------------------------------------------------

## Expected Repository Artifacts

``` text
backend/
├── providers/
├── ingestion/
├── api/
├── models/
└── repositories/

docs/
├── architecture/
│   ├── ERD.md
│   ├── Provider_Contracts.md
│   └── Sequence_Diagrams.md
│
└── api/
    └── OpenAPI.md
```
