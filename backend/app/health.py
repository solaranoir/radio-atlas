from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class HealthStatus(StrEnum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


@dataclass
class ProviderHealth:
    provider: str
    status: HealthStatus = HealthStatus.UNKNOWN
    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None
    last_error: str | None = None

    def record_success(self) -> None:
        self.status = HealthStatus.HEALTHY
        self.last_success_at = datetime.now(UTC)
        self.last_error = None

    def record_failure(
        self,
        error: Exception,
    ) -> None:
        self.status = HealthStatus.UNHEALTHY
        self.last_failure_at = datetime.now(UTC)
        self.last_error = str(error)


noaa_health = ProviderHealth(
    provider="noaa",
)

psk_reporter_health = ProviderHealth(
    provider="psk_reporter",
)
