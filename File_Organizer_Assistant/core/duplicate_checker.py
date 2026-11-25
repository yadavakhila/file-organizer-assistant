"""Duplicate filename and SHA-256 content detection."""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from core.scanner import ScannedFile
from utils.file_utils import compute_sha256


class DuplicateChecker:
    """Detects duplicate filenames, destination conflicts, and identical file contents."""

    def find_filename_duplicates(self, files: List[ScannedFile]) -> Dict[str, List[ScannedFile]]:
        """Group scanned files by lowercase filename when count > 1."""
        groups: Dict[str, List[ScannedFile]] = defaultdict(list)
        for item in files:
            groups[item.file_name.lower()].append(item)
        return {name: items for name, items in groups.items() if len(items) > 1}

    def check_content_match(self, path_a: Path, path_b: Path) -> bool:
        """Compare two files using SHA-256 hashes. Returns False if either cannot be read."""
        if not path_a.is_file() or not path_b.is_file():
            return False
        try:
            if path_a.stat().st_size != path_b.stat().st_size:
                return False
        except OSError:
            return False

        hash_a = compute_sha256(path_a)
        hash_b = compute_sha256(path_b)
        return bool(hash_a and hash_b and hash_a == hash_b)

    def find_content_duplicates(self, files: List[ScannedFile]) -> Dict[str, List[ScannedFile]]:
        """Group files with identical SHA-256 content hashes."""
        size_groups: Dict[int, List[ScannedFile]] = defaultdict(list)
        for f in files:
            size_groups[f.file_size].append(f)

        hash_groups: Dict[str, List[ScannedFile]] = defaultdict(list)
        for same_size_files in size_groups.values():
            if len(same_size_files) < 2:
                continue
            for item in same_size_files:
                digest = compute_sha256(Path(item.source_path))
                if digest:
                    hash_groups[digest].append(item)

        return {h: items for h, items in hash_groups.items() if len(items) > 1}
