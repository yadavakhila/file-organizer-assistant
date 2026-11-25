"""Organization history persistence manager supporting safe undo."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import HISTORY_PATH
from utils.logger import get_logger

logger = get_logger("history_manager")


class HistoryManager:
    """Stores and retrieves organization batch history in organization_history.json."""

    def __init__(self, history_path: Path | None = None) -> None:
        self.history_path = history_path or HISTORY_PATH

    def load_history(self) -> List[Dict[str, Any]]:
        """Load organization history list safely."""
        if not self.history_path.exists():
            self.save_history([])
            return []
        try:
            raw = self.history_path.read_text(encoding="utf-8")
            if not raw.strip():
                return []
            payload = json.loads(raw)
            if isinstance(payload, dict) and isinstance(payload.get("history"), list):
                return [item for item in payload["history"] if isinstance(item, dict)]
            raise ValueError("Malformed history JSON structure.")
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            logger.error("Corrupted history JSON (%s): %s", self.history_path, exc)
            self.save_history([])
            return []

    def save_history(self, history: List[Dict[str, Any]]) -> bool:
        """Persist history list to JSON."""
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            self.history_path.write_text(
                json.dumps({"history": history}, indent=2), encoding="utf-8"
            )
            return True
        except OSError as exc:
            logger.error("Failed to save history JSON: %s", exc)
            return False

    def add_operation(self, operation_entry: Dict[str, Any]) -> None:
        """Append an organization operation batch to history."""
        history = self.load_history()
        history.append(operation_entry)
        self.save_history(history)

    def get_last_undoable_operation(self) -> Optional[Dict[str, Any]]:
        """Return the most recent operation that has movements and has not been undone."""
        history = self.load_history()
        for entry in reversed(history):
            if not entry.get("undone", False) and entry.get("movements"):
                return entry
        return None

    def mark_undone(self, operation_id: str) -> bool:
        """Mark a specific operation ID as undone."""
        history = self.load_history()
        updated = False
        for entry in history:
            if entry.get("operation_id") == operation_id:
                entry["undone"] = True
                updated = True
                break
        if updated:
            self.save_history(history)
        return updated
