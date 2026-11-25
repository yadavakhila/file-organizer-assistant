"""JSON persistence manager with corruption recovery and schema validation."""

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from config.settings import DEFAULT_SETTINGS, FILE_RECORDS_PATH, SETTINGS_PATH
from utils.logger import get_logger

logger = get_logger("json_manager")

REQUIRED_RECORD_KEYS = {
    "file_name",
    "extension",
    "category",
    "file_size",
    "source_path",
    "destination_path",
    "status",
    "date_scanned",
}


class JSONManager:
    """Handles safe loading and saving of file_records.json and settings.json."""

    def __init__(
        self,
        records_path: Path | None = None,
        settings_path: Path | None = None,
    ) -> None:
        self.records_path = records_path or FILE_RECORDS_PATH
        self.settings_path = settings_path or SETTINGS_PATH

    def load_records(self) -> List[Dict[str, Any]]:
        """Load and validate file records, recovering gracefully if missing or corrupted."""
        if not self.records_path.exists():
            self.save_records([])
            return []

        try:
            raw = self.records_path.read_text(encoding="utf-8")
            if not raw.strip():
                return []
            payload = json.loads(raw)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Corrupted or unreadable records JSON (%s): %s", self.records_path, exc)
            self._backup_corrupted(self.records_path)
            self.save_records([])
            return []

        if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
            logger.warning("Malformed records structure in %s; resetting.", self.records_path)
            self._backup_corrupted(self.records_path)
            self.save_records([])
            return []

        valid_records: List[Dict[str, Any]] = []
        seen_keys = set()
        for item in payload["records"]:
            if not isinstance(item, dict):
                continue
            if not REQUIRED_RECORD_KEYS.issubset(item.keys()):
                continue
            dedup_key = (
                str(item.get("source_path", "")),
                str(item.get("destination_path", "")),
                str(item.get("status", "")),
                str(item.get("date_scanned", "")),
            )
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)
            valid_records.append(item)

        return valid_records

    def save_records(self, records: List[Dict[str, Any]]) -> bool:
        """Persist file records atomically to JSON."""
        try:
            self.records_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"records": records}
            self.records_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return True
        except OSError as exc:
            logger.error("Failed to save records JSON: %s", exc)
            return False

    def append_records(self, new_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Append new records while preventing duplicates."""
        existing = self.load_records()
        seen = {
            (
                str(r.get("source_path", "")),
                str(r.get("destination_path", "")),
                str(r.get("status", "")),
                str(r.get("date_scanned", "")),
            )
            for r in existing
        }
        for rec in new_records:
            if not REQUIRED_RECORD_KEYS.issubset(rec.keys()):
                continue
            key = (
                str(rec.get("source_path", "")),
                str(rec.get("destination_path", "")),
                str(rec.get("status", "")),
                str(rec.get("date_scanned", "")),
            )
            if key not in seen:
                seen.add(key)
                existing.append(rec)
        self.save_records(existing)
        return existing

    def load_settings(self) -> Dict[str, Any]:
        """Load application settings, falling back to defaults if missing/corrupted."""
        if not self.settings_path.exists():
            defaults = deepcopy(DEFAULT_SETTINGS)
            self.save_settings(defaults)
            return defaults

        try:
            raw = self.settings_path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Settings root must be a JSON object.")
            merged = deepcopy(DEFAULT_SETTINGS)
            merged.update(data)
            return merged
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            logger.error("Corrupted settings JSON (%s): %s", self.settings_path, exc)
            self._backup_corrupted(self.settings_path)
            defaults = deepcopy(DEFAULT_SETTINGS)
            self.save_settings(defaults)
            return defaults

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Persist settings dictionary to JSON."""
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            self.settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
            return True
        except OSError as exc:
            logger.error("Failed to save settings JSON: %s", exc)
            return False

    @staticmethod
    def _backup_corrupted(path: Path) -> None:
        try:
            backup = path.with_suffix(path.suffix + ".bak")
            if path.exists():
                backup.write_bytes(path.read_bytes())
        except OSError:
            pass
