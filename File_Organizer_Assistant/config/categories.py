"""Default file classification categories and extension mappings."""

from typing import Dict, List

DEFAULT_CATEGORIES: Dict[str, List[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".md"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Programming": [".py", ".c", ".cpp", ".java", ".js", ".html", ".css", ".php"],
    "Spreadsheets": [".csv", ".xls", ".xlsx"],
    "Executables": [".exe", ".msi"],
}

OTHERS_CATEGORY = "Others"


def build_extension_map(categories: Dict[str, List[str]]) -> Dict[str, str]:
    """Build a lowercase extension -> category lookup dictionary."""
    ext_map: Dict[str, str] = {}
    for category, extensions in categories.items():
        for ext in extensions:
            normalized = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            ext_map[normalized] = category
    return ext_map
