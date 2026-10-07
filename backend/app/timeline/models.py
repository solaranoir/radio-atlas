import json
from datetime import UTC, datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field, JsonValue, field_validator, model_validator

Resolution = Literal["minute", "hour", "day"]
Coverage = Literal["all_observations", "band_resolved_observations"]
MAX_SAFE_COUNT = 2**53 - 1


class UTCModel(BaseModel):
    @field_validator("*", mode="after")
    @classmethod
    def normalize_datetime(cls, value: object) -> object:
        return value.astimezone(UTC) if isinstance(value, datetime) else value


class HistoryBounds(UTCModel):
    start_time: AwareDatetime | None
    end_time: AwareDatetime | None


class TimelineBucket(UTCModel):
    start_time: AwareDatetime
    end_time: AwareDatetime
    observation_count: int = Field(ge=0, le=MAX_SAFE_COUNT)
    normalized_density: float = Field(ge=0, le=1, allow_inf_nan=False)

    @model_validator(mode="after")
    def valid_interval(self) -> "TimelineBucket":
        if self.start_time >= self.end_time:
            raise ValueError("Bucket end must be after start")
        return self


class TimelineEvent(UTCModel):
    id: str = Field(min_length=1)
    event_type: str = Field(default="activity_peak", min_length=1)
    source: str = Field(default="timeline_activity", min_length=1)
    start_time: AwareDatetime
    end_time: AwareDatetime | None = None
    severity: Literal["info", "low", "medium", "high"] = "info"
    label: str = Field(default="Elevated radio activity", max_length=160)
    observation_count: int | None = Field(default=None, ge=0, le=MAX_SAFE_COUNT)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("metadata")
    @classmethod
    def bounded_metadata(cls, value: dict[str, JsonValue]) -> dict[str, JsonValue]:
        if len(json.dumps(value, allow_nan=False, separators=(",", ":")).encode()) > 4096:
            raise ValueError("Marker metadata exceeds 4 KiB")
        return value

    @model_validator(mode="after")
    def valid_interval(self) -> "TimelineEvent":
        if self.end_time is not None and self.start_time >= self.end_time:
            raise ValueError("Event end must be after start")
        return self


class TimelineResponse(UTCModel):
    schema_version: Literal[1] = 1
    generated_at: AwareDatetime
    history: HistoryBounds
    start_time: AwareDatetime | None
    end_time: AwareDatetime | None
    source_resolution: Resolution | None
    bucket_seconds: int | None
    density_coverage: Coverage | None
    aggregation_status: Literal["unknown", "not_applicable"]
    buckets: list[TimelineBucket] = Field(default_factory=list)
    events: list[TimelineEvent] = Field(default_factory=list)
    next_event_cursor: str | None = None
