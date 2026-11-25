"""Safe file organization and undo engine."""

import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

from core.preview import PreviewItem, PreviewSummary
from utils.date_utils import now_iso, today_date
from utils.file_utils import ensure_directory
from utils.logger import get_logger

logger = get_logger("organizer")


@dataclass
class OrganizationOperationRecord:
    """Represents the result of processing a single file during organization."""

    file_name: str
    extension: str
    category: str
    file_size: int
    source_path: str
    destination_path: str
    status: str  # "Organized", "Skipped", "Failed"
    date_scanned: str
    message: str


@dataclass
class OrganizationResult:
    """Summary of an executed organization batch."""

    operation_id: str
    timestamp: str
    target_directory: str
    total_attempted: int
    organized_count: int
    skipped_count: int
    failed_count: int
    records: List[OrganizationOperationRecord]
    movements: List[Dict[str, str]]  # For safe undo


class FileOrganizer:
    """Executes confirmed file movements safely and supports undoing the last batch."""

    def organize(
        self,
        preview: PreviewSummary,
        confirmed: bool,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> OrganizationResult:
        """
        Execute file movements from a PreviewSummary.

        Raises PermissionError / ValueError if not explicitly confirmed.
        """
        if not confirmed:
            raise ValueError("Organization cannot run without explicit user confirmation.")

        operation_id = f"OP-{uuid.uuid4().hex[:8].upper()}"
        timestamp = now_iso()
        records: List[OrganizationOperationRecord] = []
        movements: List[Dict[str, str]] = []

        organized_count = 0
        skipped_count = 0
        failed_count = 0
        total_items = len(preview.items)

        for idx, item in enumerate(preview.items, start=1):
            if progress_callback:
                progress_callback(idx, total_items, item.file_name)

            if item.action != "Move":
                skipped_count += 1
                records.append(self._to_record(item, "Skipped", item.reason))
                continue

            src = Path(item.source_path)
            dst = Path(item.proposed_destination)

            if not src.exists():
                failed_count += 1
                msg = f"Source file no longer exists: {src}"
                logger.error(msg)
                records.append(self._to_record(item, "Failed", msg))
                continue

            if dst.exists():
                skipped_count += 1
                msg = f"Destination already exists, skipped safely: {dst}"
                logger.warning(msg)
                records.append(self._to_record(item, "Skipped", msg))
                continue

            try:
                ensure_directory(dst.parent)
                shutil.move(str(src), str(dst))
                organized_count += 1
                records.append(self._to_record(item, "Organized", "Moved successfully."))
                movements.append(
                    {
                        "file_name": item.file_name,
                        "category": item.category,
                        "original_path": str(src),
                        "new_path": str(dst),
                        "status": "Organized",
                    }
                )
            except PermissionError as exc:
                failed_count += 1
                msg = f"Permission denied moving {src.name}: {exc}"
                logger.error(msg)
                records.append(self._to_record(item, "Failed", msg))
            except OSError as exc:
                failed_count += 1
                msg = f"OS error moving {src.name}: {exc}"
                logger.error(msg)
                records.append(self._to_record(item, "Failed", msg))

        logger.info(
            "Organization %s complete for '%s': organized=%d, skipped=%d, failed=%d",
            operation_id,
            preview.target_directory,
            organized_count,
            skipped_count,
            failed_count,
        )

        return OrganizationResult(
            operation_id=operation_id,
            timestamp=timestamp,
            target_directory=preview.target_directory,
            total_attempted=total_items,
            organized_count=organized_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            records=records,
            movements=movements,
        )

    def undo_movements(self, movements: List[Dict[str, str]]) -> Dict[str, object]:
        """
        Safely reverse a list of recorded movements without overwriting existing files.

        Returns a dict with counts and lists of restored/skipped/failed paths.
        """
        restored: List[str] = []
        skipped: List[str] = []
        failed: List[str] = []

        for move in reversed(movements):
            current_path = Path(move.get("new_path", ""))
            original_path = Path(move.get("original_path", ""))

            if not current_path.exists():
                skipped.append(f"Missing moved file: {current_path}")
                continue
            if original_path.exists():
                skipped.append(f"Original location occupied (no overwrite): {original_path}")
                continue

            try:
                ensure_directory(original_path.parent)
                shutil.move(str(current_path), str(original_path))
                restored.append(str(original_path))
                # Clean up empty category folder if it became empty
                try:
                    if current_path.parent.exists() and not any(current_path.parent.iterdir()):
                        current_path.parent.rmdir()
                except OSError:
                    pass
            except (PermissionError, OSError) as exc:
                failed.append(f"Failed restoring {current_path.name}: {exc}")

        logger.info(
            "Undo completed: restored=%d, skipped=%d, failed=%d",
            len(restored),
            len(skipped),
            len(failed),
        )
        return {
            "restored_count": len(restored),
            "skipped_count": len(skipped),
            "failed_count": len(failed),
            "restored": restored,
            "skipped": skipped,
            "failed": failed,
            "timestamp": today_date(),
        }

    @staticmethod
    def _to_record(item: PreviewItem, status: str, message: str) -> OrganizationOperationRecord:
        return OrganizationOperationRecord(
            file_name=item.file_name,
            extension=item.extension,
            category=item.category,
            file_size=item.file_size,
            source_path=item.source_path,
            destination_path=item.proposed_destination,
            status=status,
            date_scanned=item.date_scanned,
            message=message,
        )
