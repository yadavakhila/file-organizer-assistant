"""Application-wide paths, constants, and default settings."""

from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

FILE_RECORDS_PATH = DATA_DIR / "file_records.json"
SETTINGS_PATH = DATA_DIR / "settings.json"
HISTORY_PATH = DATA_DIR / "organization_history.json"
ACTIVITY_LOG_PATH = DATA_DIR / "activity_log.csv"
APP_LOG_PATH = LOGS_DIR / "application.log"

APP_NAME = "File Organizer Assistant"
APP_VERSION = "1.0.0"
PROJECT_CODE = "SmartCommunity Hack - Project #105"

DEFAULT_SETTINGS: Dict[str, Any] = {
    "include_subfolders": False,
    "include_hidden_files": False,
    "conflict_policy": "skip",  # "skip" or "rename"
    "check_sha256_duplicates": True,
    "theme": "dark",
    "custom_categories": {},
    "category_folder_names": {},
}

# Protected system directories that must never be organized automatically
PROTECTED_DIR_NAMES = {
    "windows",
    "system32",
    "program files",
    "program files (x86)",
    "programdata",
    "usr",
    "bin",
    "sbin",
    "etc",
    "var",
    "boot",
    "dev",
    "proc",
    "sys",
    "library",
    "system",
}
