"""Unit tests for PreviewEngine and DuplicateChecker."""

import tempfile
import unittest
from pathlib import Path

from core.classifier import FileClassifier
from core.duplicate_checker import DuplicateChecker
from core.preview import PreviewEngine
from core.scanner import FileScanner


class TestPreviewAndDuplicates(unittest.TestCase):
    def test_preview_is_non_destructive_and_detects_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f1 = root / "report.pdf"
            f1.write_text("same content", encoding="utf-8")

            docs_dir = root / "Documents"
            docs_dir.mkdir()
            existing = docs_dir / "report.pdf"
            existing.write_text("same content", encoding="utf-8")

            f2 = root / "photo.png"
            f2.write_text("img", encoding="utf-8")

            scan_res = FileScanner().scan(tmp)
            preview = PreviewEngine(FileClassifier()).generate_preview(
                scan_res, conflict_policy="skip", check_sha256=True
            )

            self.assertEqual(preview.total_scanned, 2)
            self.assertEqual(preview.ready_to_move, 1)
            self.assertEqual(preview.conflicts_count, 1)
            self.assertEqual(preview.skipped_count, 1)

            # Verify no files were moved or deleted during preview
            self.assertTrue(f1.exists())
            self.assertTrue(f2.exists())
            self.assertFalse((root / "Images" / "photo.png").exists())

    def test_duplicate_checker_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = root / "a.txt"
            b = root / "b.txt"
            a.write_text("identical bytes", encoding="utf-8")
            b.write_text("identical bytes", encoding="utf-8")
            self.assertTrue(DuplicateChecker().check_content_match(a, b))


if __name__ == "__main__":
    unittest.main()
