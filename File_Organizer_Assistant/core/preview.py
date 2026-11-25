"""Non-destructive preview engine for proposed file organization."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

from core.classifier import FileClassifier
from core.conflict_handler import ConflictHandler
from core.scanner import ScanResult
from utils.logger import get_logger

logger = get_logger("preview")


@dataclass
class PreviewItem:
    """Represents a single proposed file movement in preview mode."""

    file_name: str
    extension: str
    category: str
    is_known_extension: bool
    file_size: int
    size_formatted: str
    modified_date: str
    date_scanned: str
    source_path: str
    proposed_destination: str
    conflict_status: str
    action: str  # "Move" or "Skip"
    reason: str


@dataclass
class PreviewSummary:
    """Complete preview output prior to user confirmation."""

    target_directory: str
    items: List[PreviewItem]
    total_scanned: int
    ready_to_move: int
    conflicts_count: int
    skipped_count: int
    total_size: int


class PreviewEngine:
    """Generates non-destructive organization previews without modifying any files."""

    def __init__(
        self,
        classifier: FileClassifier,
        conflict_handler: ConflictHandler | None = None,
    ) -> None:
        self.classifier = classifier
        self.conflict_handler = conflict_handler or ConflictHandler()

    def generate_preview(
        self,
        scan_result: ScanResult,
        conflict_policy: str = "skip",
        check_sha256: bool = True,
    ) -> PreviewSummary:
        """Build a PreviewSummary from a ScanResult without touching the filesystem."""
        root = Path(scan_result.target_directory)
        planned_destinations: Set[str] = set()
        items: List[PreviewItem] = []

        ready_count = 0
        conflict_count = 0
        skipped_count = 0

        for scanned in scan_result.files:
            source = Path(scanned.source_path)
            category, is_known = self.classifier.classify_extension(scanned.extension)
            folder_name = self.classifier.get_folder_name(category)
            proposed_dest = root / folder_name / scanned.file_name

            conflict_status, detail = self.conflict_handler.evaluate_destination(
                source,
                proposed_dest,
                planned_destinations,
                check_sha256=check_sha256,
            )

            if conflict_status == "None":
                action = "Move"
                final_dest = proposed_dest
                planned_destinations.add(str(final_dest).lower())
                ready_count += 1
            elif conflict_status == "Already Organized":
                action = "Skip"
                final_dest = proposed_dest
                skipped_count += 1
            else:
                conflict_count += 1
                if conflict_policy == "rename":
                    final_dest = self.conflict_handler.generate_safe_name(
                        proposed_dest, planned_destinations
                    )
                    action = "Move"
                    detail = f"{detail} Will rename to '{final_dest.name}'."
                    planned_destinations.add(str(final_dest).lower())
                    ready_count += 1
                else:
                    action = "Skip"
                    final_dest = proposed_dest
                    skipped_count += 1

            items.append(
                PreviewItem(
                    file_name=scanned.file_name,
                    extension=scanned.extension,
                    category=category,
                    is_known_extension=is_known,
                    file_size=scanned.file_size,
                    size_formatted=scanned.size_formatted,
                    modified_date=scanned.modified_date,
                    date_scanned=scanned.date_scanned,
                    source_path=scanned.source_path,
                    proposed_destination=str(final_dest),
                    conflict_status=conflict_status,
                    action=action,
                    reason=detail,
                )
            )

        logger.info(
            "Generated preview for '%s': total=%d, ready=%d, conflicts=%d, skipped=%d",
            scan_result.target_directory,
            len(items),
            ready_count,
            conflict_count,
            skipped_count,
        )
        return PreviewSummary(
            target_directory=scan_result.target_directory,
            items=items,
            total_scanned=len(items),
            ready_to_move=ready_count,
            conflicts_count=conflict_count,
            skipped_count=skipped_count,
            total_size=scan_result.total_size,
        )
