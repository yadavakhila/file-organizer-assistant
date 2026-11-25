"""Centralized defensive input and path validation."""

import os
import re
from pathlib import Path
from typing import Tuple

from config.settings import PROTECTED_DIR_NAMES

CATEGORY_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _-]{0,48}$")
EXTENSION_PATTERN = re.compile(r"^\.?[A-Za-z0-9]{1,15}$")
INVALID_WIN_CHARS = set('<>:"/\\|?*')


def validate_directory_path(raw_path: str) -> Tuple[bool, str, Path | None]:
    """Validate that a user-supplied path is an accessible, non-protected directory."""
    if not raw_path or not raw_path.strip():
        return False, "Directory path cannot be empty.", None

    cleaned = raw_path.strip().strip('"').strip("'")
    try:
        path = Path(cleaned).expanduser().resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        return False, f"Invalid path syntax: {exc}", None

    if not path.exists():
        return False, f"Directory does not exist: {path}", None
    if not path.is_dir():
        return False, f"Path is not a directory: {path}", None

    # Block filesystem root or protected OS directories
    if path == path.parent:
        return False, "Cannot organize a filesystem root directory.", None

    lowered_parts = {part.lower() for part in path.parts}
    if path.name.lower() in PROTECTED_DIR_NAMES or (
        len(path.parts) <= 3 and bool(lowered_parts & PROTECTED_DIR_NAMES)
    ):
        return False, f"Protected system directory cannot be organized: {path}", None

    if not os.access(path, os.R_OK):
        return False, f"Directory is not readable (permission denied): {path}", None

    return True, "Valid directory.", path


def validate_category_name(name: str) -> Tuple[bool, str, str]:
    """Validate a category or destination folder name."""
    if not name or not name.strip():
        return False, "Category name cannot be empty.", ""
    cleaned = name.strip()
    if any(ch in INVALID_WIN_CHARS for ch in cleaned):
        return False, "Category name contains invalid filesystem characters.", ""
    if not CATEGORY_NAME_PATTERN.match(cleaned):
        return (
            False,
            "Category name must start with a letter/digit and use only letters, digits, spaces, _ or -.",
            "",
        )
    return True, "Valid category name.", cleaned


def validate_extension(ext: str) -> Tuple[bool, str, str]:
    """Validate and normalize a file extension (e.g. 'jpg' or '.JPG' -> '.jpg')."""
    if not ext or not ext.strip():
        return False, "Extension cannot be empty.", ""
    cleaned = ext.strip()
    if not EXTENSION_PATTERN.match(cleaned):
        return False, "Extension must be 1-15 alphanumeric characters (e.g. .pdf or pdf).", ""
    normalized = cleaned.lower() if cleaned.startswith(".") else f".{cleaned.lower()}"
    return True, "Valid extension.", normalized


def validate_export_path(raw_path: str) -> Tuple[bool, str, Path | None]:
    """Validate an export file or directory destination."""
    if not raw_path or not raw_path.strip():
        return False, "Export path cannot be empty.", None
    cleaned = raw_path.strip().strip('"').strip("'")
    try:
        path = Path(cleaned).expanduser().resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        return False, f"Invalid export path: {exc}", None

    parent = path if path.is_dir() else path.parent
    if not parent.exists():
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return False, f"Cannot create export directory: {exc}", None
    return True, "Valid export path.", path


def validate_confirmation(response: str) -> bool:
    """Return True only for explicit affirmative confirmation."""
    return response.strip().lower() in {"y", "yes", "confirm"}
