from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


class NormalizationError(ValueError):
    """Raised when extracted booking data cannot be normalized safely."""


def normalize_datetime(
    date_value: str | None,
    time_value: str | None,
    timezone: str,
    *,
    now: datetime | None = None,
) -> datetime:
    if not date_value:
        raise NormalizationError("date is required")

    if not time_value:
        raise NormalizationError("time is required")

    try:
        tz = ZoneInfo(timezone)
    except Exception as exc:
        raise NormalizationError(f"invalid timezone: {timezone}") from exc

    current = now or datetime.now(tz)

    normalized_date = _normalize_date(date_value, current)
    normalized_time = _normalize_time(time_value)

    local_dt = datetime.combine(
        normalized_date,
        normalized_time,
        tzinfo=tz,
    )

    return local_dt.astimezone(ZoneInfo("UTC"))


def _normalize_date(value: str, current: datetime):
    value = value.strip().lower()

    if value == "today":
        return current.date()

    if value == "tomorrow":
        return current.date() + timedelta(days=1)

    if value in {"بعد أسبوع", "بعد اسبوع", "in a week"}:
        return current.date() + timedelta(days=7)

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise NormalizationError(f"unsupported date: {value}") from exc


def _normalize_time(value: str) -> time:
    value = value.strip().lower()

    if ":" in value:
        try:
            parsed = datetime.strptime(value, "%H:%M").time()
        except ValueError as exc:
            raise NormalizationError(f"invalid time: {value}") from exc

        return parsed

    if value.isdigit():
        hour = int(value)

        if hour < 0 or hour > 23:
            raise NormalizationError(f"invalid hour: {value}")

        if 1 <= hour <= 12:
            raise NormalizationError(
                f"ambiguous time: {value}; AM/PM is required"
            )

        return time(hour=hour)

    raise NormalizationError(f"unsupported time: {value}")
