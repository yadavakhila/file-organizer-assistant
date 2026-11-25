"""Date and timestamp formatting utilities."""

from datetime import datetime


def now_iso() -> str:
    """Return current local timestamp as ISO-like string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_date() -> str:
    """Return current local date as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")


def format_timestamp(ts: float) -> str:
    """Format a POSIX timestamp to YYYY-MM-DD HH:MM:SS."""
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except (OSError, OverflowError, ValueError):
        return "Unknown"


def timestamp_slug() -> str:
    """Return a filesystem-safe timestamp slug for export filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
