"""Filesystem helper utilities."""

import hashlib
from pathlib import Path
from typing import Optional


def format_size(size_bytes: int) -> str:
    """Convert byte count into a human-readable string."""
    if size_bytes < 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size_bytes)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{value:.2f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024.0
    return f"{size_bytes} B"


def compute_sha256(file_path: Path, chunk_size: int = 65536) -> Optional[str]:
    """Compute SHA-256 hex digest of a file safely, returning None on error."""
    hasher = hashlib.sha256()
    try:
        with file_path.open("rb") as handle:
            while True:
                chunk = handle.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return None


def is_hidden_path(path: Path) -> bool:
    """Check if a file or any of its relative parts starts with a dot."""
    return path.name.startswith(".")


def ensure_directory(path: Path) -> Path:
    """Ensure a directory exists and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path
