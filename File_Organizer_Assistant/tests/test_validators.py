"""Unit tests for centralized input and path validation."""

import tempfile
import unittest
from pathlib import Path

from utils.validators import (
    validate_category_name,
    validate_confirmation,
    validate_directory_path,
    validate_extension,
)


class TestValidators(unittest.TestCase):
    def test_valid_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ok, _msg, path = validate_directory_path(tmp)
            self.assertTrue(ok)
            self.assertEqual(path, Path(tmp).resolve())

    def test_invalid_or_missing_directory(self) -> None:
        ok, _msg, path = validate_directory_path("")
        self.assertFalse(ok)
        self.assertIsNone(path)

        ok2, _msg2, path2 = validate_directory_path("Z:/nonexistent_dir_xyz_999")
        self.assertFalse(ok2)
        self.assertIsNone(path2)

    def test_protected_system_directory_blocked(self) -> None:
        ok, msg, _ = validate_directory_path("C:/Windows")
        if Path("C:/Windows").exists():
            self.assertFalse(ok)
            self.assertIn("Protected", msg)

    def test_category_name_validation(self) -> None:
        ok, _, clean = validate_category_name("My Reports")
        self.assertTrue(ok)
        self.assertEqual(clean, "My Reports")

        ok_bad, _, _ = validate_category_name("Bad/Name*")
        self.assertFalse(ok_bad)

    def test_extension_validation(self) -> None:
        ok, _, ext = validate_extension("JPG")
        self.assertTrue(ok)
        self.assertEqual(ext, ".jpg")

        ok_bad, _, _ = validate_extension("invalid ext!")
        self.assertFalse(ok_bad)

    def test_confirmation_validation(self) -> None:
        self.assertTrue(validate_confirmation("yes"))
        self.assertTrue(validate_confirmation("Y"))
        self.assertFalse(validate_confirmation("no"))
        self.assertFalse(validate_confirmation(""))


if __name__ == "__main__":
    unittest.main()
