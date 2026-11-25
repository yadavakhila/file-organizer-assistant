"""Unit tests for FileScanner."""

import tempfile
import unittest
from pathlib import Path

from core.scanner import FileScanner


class TestFileScanner(unittest.TestCase):
    def setUp(self) -> None:
        self.scanner = FileScanner()

    def test_empty_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            res = self.scanner.scan(tmp)
            self.assertEqual(len(res.files), 0)
            self.assertEqual(res.total_size, 0)

    def test_scan_hundreds_of_files_and_subfolders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for i in range(150):
                (root / f"file_{i}.txt").write_text("hello", encoding="utf-8")
            sub = root / "nested"
            sub.mkdir()
            (sub / "nested_doc.pdf").write_text("pdf", encoding="utf-8")
            (root / ".hidden_file").write_text("secret", encoding="utf-8")

            top_only = self.scanner.scan(tmp, include_subfolders=False, include_hidden=False)
            self.assertEqual(len(top_only.files), 150)

            with_sub = self.scanner.scan(tmp, include_subfolders=True, include_hidden=True)
            self.assertEqual(len(with_sub.files), 152)

    def test_invalid_directory_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.scanner.scan("non_existent_folder_abc_123")


if __name__ == "__main__":
    unittest.main()
