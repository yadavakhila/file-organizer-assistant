"""CSV persistence manager for activity logs and bulk CSV record import."""

import csv
from pathlib import Path
from typing import Any, Dict, List

from config.settings import ACTIVITY_LOG_PATH
from utils.date_utils import now_iso
from utils.logger import get_logger

logger = get_logger("csv_manager")

ACTIVITY_HEADERS = ["timestamp", "action", "file_name", "category", "status"]


class CSVManager:
    """Manages activity_log.csv and optional bulk CSV record imports."""

    def __init__(self, activity_log_path: Path | None = None) -> None:
        self.activity_log_path = activity_log_path or ACTIVITY_LOG_PATH

    def ensure_log_file(self) -> None:
        """Create activity_log.csv with headers if it does not exist."""
        self.activity_log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.activity_log_path.exists():
            with self.activity_log_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(ACTIVITY_HEADERS)

    def log_activity(
        self,
        action: str,
        file_name: str,
        category: str,
        status: str,
        timestamp: str | None = None,
    ) -> bool:
        """Append a single activity row to activity_log.csv."""
        try:
            self.ensure_log_file()
            with self.activity_log_path.open("a", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow([timestamp or now_iso(), action, file_name, category, status])
            return True
        except OSError as exc:
            logger.error("Failed to write activity_log.csv: %s", exc)
            return False

    def log_activities(self, rows: List[List[str]]) -> bool:
        """Append multiple activity rows efficiently."""
        if not rows:
            return True
        try:
            self.ensure_log_file()
            with self.activity_log_path.open("a", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerows(rows)
            return True
        except OSError as exc:
            logger.error("Failed to batch-write activity_log.csv: %s", exc)
            return False

    def load_activities(self, limit: int | None = None) -> List[Dict[str, str]]:
        """Read activity rows from activity_log.csv (most recent last or sliced)."""
        if not self.activity_log_path.exists():
            self.ensure_log_file()
            return []
        try:
            with self.activity_log_path.open("r", newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                rows = [dict(row) for row in reader if row.get("file_name")]
            if limit is not None and limit > 0:
                return rows[-limit:]
            return rows
        except OSError as exc:
            logger.error("Failed to read activity_log.csv: %s", exc)
            return []

    def import_records_from_csv(self, csv_path: Path) -> List[Dict[str, Any]]:
        """Import file records from an external CSV file for bulk loading."""
        imported: List[Dict[str, Any]] = []
        if not csv_path.exists() or not csv_path.is_file():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        with csv_path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row.get("file_name"):
                    continue
                try:
                    size_val = int(row.get("file_size", 0) or 0)
                except ValueError:
                    size_val = 0
                imported.append(
                    {
                        "file_name": row.get("file_name", "").strip(),
                        "extension": row.get("extension", "").strip().lower(),
                        "category": row.get("category", "Others").strip() or "Others",
                        "file_size": max(0, size_val),
                        "source_path": row.get("source_path", "").strip(),
                        "destination_path": row.get("destination_path", "").strip(),
                        "status": row.get("status", "Scanned").strip() or "Scanned",
                        "date_scanned": row.get("date_scanned", now_iso()[:10]).strip(),
                    }
                )
        return imported
