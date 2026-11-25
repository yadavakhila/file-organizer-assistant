"""Unit tests for JSONManager, CSVManager, and HistoryManager."""

import tempfile
import unittest
from pathlib import Path

from database.csv_manager import CSVManager
from database.history_manager import HistoryManager
from database.json_manager import JSONManager


class TestDatabase(unittest.TestCase):
    def test_missing_and_corrupted_json_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rec_path = root / "records.json"
            set_path = root / "settings.json"
            jm = JSONManager(records_path=rec_path, settings_path=set_path)

            # Missing files recover cleanly
            self.assertEqual(jm.load_records(), [])
            settings = jm.load_settings()
            self.assertIn("conflict_policy", settings)

            # Corrupted JSON recovers cleanly
            rec_path.write_text("{broken json!!!", encoding="utf-8")
            set_path.write_text("[not an object]", encoding="utf-8")
            self.assertEqual(jm.load_records(), [])
            self.assertIn("theme", jm.load_settings())

    def test_csv_log_and_bulk_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "activity_log.csv"
            cm = CSVManager(activity_log_path=log_path)
            cm.log_activity("MOVE", "test.pdf", "Documents", "Success")
            rows = cm.load_activities()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["file_name"], "test.pdf")

            bulk_csv = root / "import.csv"
            bulk_csv.write_text(
                "file_name,extension,category,file_size,source_path,destination_path,status,date_scanned\n"
                "a.pdf,.pdf,Documents,1024,src/a.pdf,dst/a.pdf,Organized,2026-11-25\n",
                encoding="utf-8",
            )
            imported = cm.import_records_from_csv(bulk_csv)
            self.assertEqual(len(imported), 1)
            self.assertEqual(imported[0]["file_size"], 1024)

    def test_history_manager(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hm = HistoryManager(history_path=Path(tmp) / "history.json")
            hm.add_operation(
                {
                    "operation_id": "OP-1",
                    "movements": [{"original_path": "a", "new_path": "b"}],
                    "undone": False,
                }
            )
            last = hm.get_last_undoable_operation()
            self.assertIsNotNone(last)
            self.assertTrue(hm.mark_undone("OP-1"))
            self.assertIsNone(hm.get_last_undoable_operation())


if __name__ == "__main__":
    unittest.main()
