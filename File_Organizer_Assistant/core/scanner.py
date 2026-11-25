"""Directory scanning module with safe error handling and progress reporting."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from utils.date_utils import format_timestamp, today_date
from utils.file_utils import format_size, is_hidden_path
from utils.logger import get_logger
from utils.validators import validate_directory_path

logger = get_logger("scanner")


@dataclass
class ScannedFile:
    """Represents metadata for a single scanned file."""

    file_name: str
    extension: str
    file_size: int
    size_formatted: str
    modified_date: str
    date_scanned: str
    source_path: str
    relative_path: str
    is_hidden: bool = False

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "file_name": self.file_name,
            "extension": self.extension,
            "file_size": self.file_size,
            "size_formatted": self.size_formatted,
            "modified_date": self.modified_date,
            "date_scanned": self.date_scanned,
            "source_path": self.source_path,
            "relative_path": self.relative_path,
            "is_hidden": self.is_hidden,
        }


@dataclass
class ScanResult:
    """Aggregated outcome of a directory scan."""

    target_directory: str
    files: List[ScannedFile]
    skipped_entries: List[str]
    errors: List[str]
    total_size: int


class FileScanner:
    """Scans a directory safely without following symlinks into unexpected paths."""

    def scan(
        self,
        directory_path: str,
        include_subfolders: bool = False,
        include_hidden: bool = False,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> ScanResult:
        """Scan the target directory and return a ScanResult."""
        is_valid, message, resolved_path = validate_directory_path(directory_path)
        if not is_valid or resolved_path is None:
            logger.warning("Scan rejected for '%s': %s", directory_path, message)
            raise ValueError(message)

        scanned_files: List[ScannedFile] = []
        skipped_entries: List[str] = []
        errors: List[str] = []
        total_size = 0
        scan_date = today_date()

        if include_subfolders:
            self._walk_recursive(
                resolved_path,
                resolved_path,
                include_hidden,
                scan_date,
                scanned_files,
                skipped_entries,
                errors,
                progress_callback,
            )
        else:
            self._scan_top_level(
                resolved_path,
                include_hidden,
                scan_date,
                scanned_files,
                skipped_entries,
                errors,
                progress_callback,
            )

        total_size = sum(f.file_size for f in scanned_files)
        logger.info(
            "Scanned '%s': %d files, %d skipped, %d errors.",
            resolved_path,
            len(scanned_files),
            len(skipped_entries),
            len(errors),
        )
        return ScanResult(
            target_directory=str(resolved_path),
            files=scanned_files,
            skipped_entries=skipped_entries,
            errors=errors,
            total_size=total_size,
        )

    def _scan_top_level(
        self,
        root: Path,
        include_hidden: bool,
        scan_date: str,
        scanned_files: List[ScannedFile],
        skipped_entries: List[str],
        errors: List[str],
        progress_callback: Optional[Callable[[int, str], None]],
    ) -> None:
        try:
            with os.scandir(root) as entries:
                for entry in entries:
                    entry_path = Path(entry.path)
                    if entry.is_symlink():
                        skipped_entries.append(f"Symlink skipped: {entry.path}")
                        continue
                    if not include_hidden and is_hidden_path(entry_path):
                        skipped_entries.append(f"Hidden entry skipped: {entry.path}")
                        continue
                    try:
                        if entry.is_file(follow_symlinks=False):
                            record = self._build_record(entry_path, root, scan_date)
                            scanned_files.append(record)
                            if progress_callback:
                                progress_callback(len(scanned_files), record.file_name)
                    except PermissionError as exc:
                        errors.append(f"Permission denied: {entry.path} ({exc})")
                    except OSError as exc:
                        errors.append(f"OS error reading {entry.path}: {exc}")
        except PermissionError as exc:
            errors.append(f"Permission denied scanning {root}: {exc}")
        except OSError as exc:
            errors.append(f"Error scanning {root}: {exc}")

    def _walk_recursive(
        self,
        root: Path,
        current: Path,
        include_hidden: bool,
        scan_date: str,
        scanned_files: List[ScannedFile],
        skipped_entries: List[str],
        errors: List[str],
        progress_callback: Optional[Callable[[int, str], None]],
    ) -> None:
        def _on_error(err: OSError) -> None:
            errors.append(f"Inaccessible folder/entry: {err.filename or current} ({err})")

        for dirpath, dirnames, filenames in os.walk(
            current, topdown=True, onerror=_on_error, followlinks=False
        ):
            dir_path = Path(dirpath)
            if not include_hidden:
                dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            # Filter out symlinked directories
            dirnames[:] = [d for d in dirnames if not (dir_path / d).is_symlink()]

            for fname in filenames:
                fpath = dir_path / fname
                if fpath.is_symlink():
                    skipped_entries.append(f"Symlink skipped: {fpath}")
                    continue
                if not include_hidden and is_hidden_path(fpath):
                    skipped_entries.append(f"Hidden file skipped: {fpath}")
                    continue
                try:
                    record = self._build_record(fpath, root, scan_date)
                    scanned_files.append(record)
                    if progress_callback:
                        progress_callback(len(scanned_files), record.file_name)
                except PermissionError as exc:
                    errors.append(f"Permission denied: {fpath} ({exc})")
                except OSError as exc:
                    errors.append(f"OS error reading {fpath}: {exc}")

    @staticmethod
    def _build_record(fpath: Path, root: Path, scan_date: str) -> ScannedFile:
        stat_info = fpath.stat()
        ext = fpath.suffix.lower() if fpath.suffix else ""
        return ScannedFile(
            file_name=fpath.name,
            extension=ext,
            file_size=stat_info.st_size,
            size_formatted=format_size(stat_info.st_size),
            modified_date=format_timestamp(stat_info.st_mtime),
            date_scanned=scan_date,
            source_path=str(fpath),
            relative_path=str(fpath.relative_to(root)),
            is_hidden=is_hidden_path(fpath),
        )
