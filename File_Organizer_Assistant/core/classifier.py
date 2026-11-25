"""Smart file classification engine with custom category and folder support."""

from collections import Counter
from typing import Dict, List, Optional, Tuple

from config.categories import DEFAULT_CATEGORIES, OTHERS_CATEGORY, build_extension_map


class FileClassifier:
    """Classifies files by extension (case-insensitive) into categories and folder names."""

    def __init__(
        self,
        custom_categories: Optional[Dict[str, List[str]]] = None,
        category_folder_names: Optional[Dict[str, str]] = None,
    ) -> None:
        self.categories: Dict[str, List[str]] = {
            cat: list(exts) for cat, exts in DEFAULT_CATEGORIES.items()
        }
        if custom_categories:
            for cat, exts in custom_categories.items():
                existing = self.categories.get(cat, [])
                merged = list(dict.fromkeys(existing + [self._norm_ext(e) for e in exts]))
                self.categories[cat] = merged

        self.category_folder_names: Dict[str, str] = dict(category_folder_names or {})
        self.extension_map: Dict[str, str] = build_extension_map(self.categories)

    @staticmethod
    def _norm_ext(ext: str) -> str:
        ext = ext.strip().lower()
        return ext if ext.startswith(".") else f".{ext}"

    def classify_extension(self, extension: str) -> Tuple[str, bool]:
        """Return (category, is_known) for a given file extension."""
        if not extension:
            return OTHERS_CATEGORY, False
        normalized = self._norm_ext(extension)
        category = self.extension_map.get(normalized)
        if category:
            return category, True
        return OTHERS_CATEGORY, False

    def get_folder_name(self, category: str) -> str:
        """Return the configured destination folder name for a category."""
        return self.category_folder_names.get(category, category)

    def get_all_categories(self) -> Dict[str, List[str]]:
        """Return a copy of all active categories and their extensions."""
        result = {cat: list(exts) for cat, exts in self.categories.items()}
        if OTHERS_CATEGORY not in result:
            result[OTHERS_CATEGORY] = []
        return result

    def summarize_extensions(self, extensions: List[str]) -> Dict[str, int]:
        """Return extension frequency counts."""
        normalized = [self._norm_ext(e) if e else "(no ext)" for e in extensions]
        return dict(Counter(normalized))
