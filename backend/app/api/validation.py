from datetime import datetime

from app.api.errors import APIError


def validate_time_range(
    start_time: datetime | None,
    end_time: datetime | None,
) -> None:
    if start_time is not None and end_time is not None and start_time > end_time:
        raise APIError(
            status_code=400,
            code="invalid_time_range",
            message="start_time must be before or equal to end_time",
        )
