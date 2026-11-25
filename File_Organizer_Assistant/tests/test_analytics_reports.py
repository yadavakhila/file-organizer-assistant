"""Unit tests for StatisticsEngine, FileSearchEngine, and ReportExportManager."""

import tempfile
import unittest
from pathlib import Path

from analytics.statistics_engine import StatisticsEngine
from core.search_engine import FileSearchEngine
from reports.export_manager import ReportExportManager


class TestAnalyticsAndReports(unittest.TestCase):
    def test_empty_dataset_handles_zero_division(self) -> None:
        m = StatisticsEngine().compute_metrics([])
        self.assertEqual(m["total_files"], 0)
        self.assertEqual(m["success_rate"], 0.0)
        self.assertEqual(m["most_common_extension"], "N/A")

    def test_search_and_export_all_formats(self) -> None:
        records = [
            {
                "file_name": "alpha.pdf",
                "extension": ".pdf",
                "category": "Documents",
                "file_size": 2000,
                "source_path": "a/alpha.pdf",
                "destination_path": "a/Documents/alpha.pdf",
                "status": "Organized",
                "date_scanned": "2026-11-25",
            },
            {
                "file_name": "beta.png",
                "extension": ".png",
                "category": "Images",
                "file_size": 4000,
                "source_path": "a/beta.png",
                "destination_path": "a/Images/beta.png",
                "status": "Skipped",
                "date_scanned": "2026-11-25",
            },
        ]
        found = FileSearchEngine().search_and_filter(records, query="alpha", category="Documents")
        self.assertEqual(len(found), 1)

        metrics = StatisticsEngine().compute_metrics(records)
        self.assertEqual(metrics["total_files"], 2)
        self.assertEqual(metrics["organized_files"], 1)
        self.assertEqual(metrics["success_rate"], 50.0)

        exporter = ReportExportManager()
        with tempfile.TemporaryDirectory() as tmp:
            for fmt in ("csv", "json", "md", "txt"):
                out = exporter.export_report(fmt, records, metrics, [], destination=tmp)
                self.assertTrue(Path(out).exists())
                self.assertGreater(Path(out).stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
