"""Safe conflict handling so existing files are never overwritten."""

from pathlib import Path
from typing import Set, Tuple

from core.duplicate_checker import DuplicateChecker


class ConflictHandler:
    """Evaluates destination conflicts and provides safe skip or rename resolutions."""

    def __init__(self, duplicate_checker: DuplicateChecker | None = None) -> None:
        self.duplicate_checker = duplicate_checker or DuplicateChecker()

    def evaluate_destination(
        self,
        source_path: Path,
        proposed_dest: Path,
        planned_destinations: Set[str],
        check_sha256: bool = True,
    ) -> Tuple[str, str]:
        """
        Evaluate whether moving source_path to proposed_dest has a conflict.

        Returns (conflict_status, detail_message) where conflict_status is one of:
        - "None"
        - "Already Organized"
        - "Destination Exists (Identical)"
        - "Destination Exists"
        - "Duplicate In Batch"
        """
        try:
            if source_path.resolve() == proposed_dest.resolve():
                return "Already Organized", "File is already in target folder."
        except OSError:
            pass

        dest_key = str(proposed_dest).lower()
        if proposed_dest.exists():
            if check_sha256 and self.duplicate_checker.check_content_match(source_path, proposed_dest):
                return "Destination Exists (Identical)", "Identical file (SHA-256 match) already exists at destination."
            return "Destination Exists", "A file with the same name already exists at destination."

        if dest_key in planned_destinations:
            return "Duplicate In Batch", "Another file in this scan targets the same destination path."

        return "None", "Ready to move."

    @staticmethod
    def generate_safe_name(proposed_dest: Path, planned_destinations: Set[str]) -> Path:
        """Generate a non-colliding alternative destination path like 'name (1).ext'."""
        stem = proposed_dest.stem
        suffix = proposed_dest.suffix
        parent = proposed_dest.parent
        counter = 1
        while True:
            candidate = parent / f"{stem} ({counter}){suffix}"
            if not candidate.exists() and str(candidate).lower() not in planned_destinations:
                return candidate
            counter += 1
