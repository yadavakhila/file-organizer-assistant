"""Unit tests for FileOrganizer, confirmation guard, repeated runs, and safe undo."""

import tempfile
import unittest
from pathlib import Path

from core.classifier import FileClassifier
from core.organizer import FileOrganizer
from core.preview import PreviewEngine
from core.scanner import FileScanner


class TestOrganizer(unittest.TestCase):
    def test_requires_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "notes.txt").write_text("abc", encoding="utf-8")
            scan_res = FileScanner().scan(tmp)
            preview = PreviewEngine(FileClassifier()).generate_preview(scan_res)

            with self.assertRaises(ValueError):
                FileOrganizer().organize(preview, confirmed=False)
            self.assertTrue((root / "notes.txt").exists())

    def test_organize_repeated_attempt_and_undo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "notes.txt").write_text("hello", encoding="utf-8")
            (root / "script.py").write_text("print(1)", encoding="utf-8")

            scanner = FileScanner()
            clf = FileClassifier()
            prev_engine = PreviewEngine(clf)
            organizer = FileOrganizer()

            scan1 = scanner.scan(tmp)
            prev1 = prev_engine.generate_preview(scan1)
            res1 = organizer.organize(prev1, confirmed=True)

            self.assertEqual(res1.organized_count, 2)
            self.assertTrue((root / "Documents" / "notes.txt").exists())
            self.assertTrue((root / "Programming" / "script.py").exists())

            # Repeated organization attempt with subfolders=True should safely skip already organized
            scan2 = scanner.scan(tmp, include_subfolders=True)
            prev2 = prev_engine.generate_preview(scan2)
            res2 = organizer.organize(prev2, confirmed=True)
            self.assertEqual(res2.organized_count, 0)
            self.assertEqual(res2.skipped_count, 2)

            # Safe undo restores files back to root
            undo_res = organizer.undo_movements(res1.movements)
            self.assertEqual(undo_res["restored_count"], 2)
            self.assertTrue((root / "notes.txt").exists())
            self.assertTrue((root / "script.py").exists())


if __name__ == "__main__":
    unittest.main()
