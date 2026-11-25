"""Custom rules and settings management for categories, extensions, and preferences."""

from copy import deepcopy
from typing import Any, Dict, List, Tuple

from config.categories import DEFAULT_CATEGORIES
from config.settings import DEFAULT_SETTINGS
from utils.validators import validate_category_name, validate_extension


class CustomRulesManager:
    """Manages user-defined categories, custom extensions, folder names, and preferences."""

    def __init__(self, settings: Dict[str, Any] | None = None) -> None:
        self.settings: Dict[str, Any] = deepcopy(DEFAULT_SETTINGS)
        if settings:
            self.settings.update(settings)
            if "custom_categories" not in self.settings or not isinstance(
                self.settings["custom_categories"], dict
            ):
                self.settings["custom_categories"] = {}
            if "category_folder_names" not in self.settings or not isinstance(
                self.settings["category_folder_names"], dict
            ):
                self.settings["category_folder_names"] = {}

    def add_custom_extension(self, category: str, extension: str) -> Tuple[bool, str]:
        """Add a validated custom extension to an existing or new category."""
        ok_cat, msg_cat, clean_cat = validate_category_name(category)
        if not ok_cat:
            return False, msg_cat

        ok_ext, msg_ext, norm_ext = validate_extension(extension)
        if not ok_ext:
            return False, msg_ext

        custom_cats: Dict[str, List[str]] = self.settings.setdefault("custom_categories", {})
        # Remove from other custom categories if reassigned
        for existing_cat, exts in custom_cats.items():
            if existing_cat != clean_cat and norm_ext in exts:
                exts.remove(norm_ext)

        cat_exts = custom_cats.setdefault(clean_cat, [])
        if norm_ext not in cat_exts:
            cat_exts.append(norm_ext)

        return True, f"Added extension '{norm_ext}' to category '{clean_cat}'."

    def create_custom_category(self, category: str, extensions: List[str] | None = None) -> Tuple[bool, str]:
        """Create a new custom category with optional initial extensions."""
        ok_cat, msg_cat, clean_cat = validate_category_name(category)
        if not ok_cat:
            return False, msg_cat

        custom_cats: Dict[str, List[str]] = self.settings.setdefault("custom_categories", {})
        if clean_cat in DEFAULT_CATEGORIES or clean_cat in custom_cats:
            return False, f"Category '{clean_cat}' already exists."

        validated_exts: List[str] = []
        for ext in extensions or []:
            ok_ext, msg_ext, norm_ext = validate_extension(ext)
            if not ok_ext:
                return False, msg_ext
            if norm_ext not in validated_exts:
                validated_exts.append(norm_ext)

        custom_cats[clean_cat] = validated_exts
        return True, f"Created custom category '{clean_cat}'."

    def rename_category_folder(self, category: str, folder_name: str) -> Tuple[bool, str]:
        """Set a custom destination folder name for a category."""
        ok_folder, msg_folder, clean_folder = validate_category_name(folder_name)
        if not ok_folder:
            return False, msg_folder

        self.settings.setdefault("category_folder_names", {})[category] = clean_folder
        return True, f"Category '{category}' will now organize into '{clean_folder}'."

    def set_preference(self, key: str, value: Any) -> Tuple[bool, str]:
        """Update a boolean or policy preference."""
        if key in {"include_subfolders", "include_hidden_files", "check_sha256_duplicates"}:
            self.settings[key] = bool(value)
            return True, f"Updated '{key}' to {bool(value)}."
        if key == "conflict_policy":
            if value not in {"skip", "rename"}:
                return False, "Conflict policy must be 'skip' or 'rename'."
            self.settings[key] = value
            return True, f"Updated conflict policy to '{value}'."
        if key == "theme":
            if value not in {"dark", "light"}:
                return False, "Theme must be 'dark' or 'light'."
            self.settings[key] = value
            return True, f"Updated theme to '{value}'."
        return False, f"Unknown setting key: {key}"

    def restore_defaults(self) -> Dict[str, Any]:
        """Reset all settings and custom rules back to defaults."""
        self.settings = deepcopy(DEFAULT_SETTINGS)
        return self.settings
