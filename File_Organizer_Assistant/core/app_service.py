"""Unified application service facade shared by both Terminal CLI and Tkinter GUI."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from analytics.statistics_engine import StatisticsEngine
from core.classifier import FileClassifier
from core.custom_rules import CustomRulesManager
from core.duplicate_checker import DuplicateChecker
from core.organizer import FileOrganizer, OrganizationResult
from core.preview import PreviewEngine, PreviewSummary
from core.scanner import FileScanner, ScanResult
from core.search_engine import FileSearchEngine
from database.csv_manager import CSVManager
from database.history_manager import HistoryManager
from database.json_manager import JSONManager
from reports.export_manager import ReportExportManager
from utils.date_utils import now_iso
from utils.logger import get_logger

logger = get_logger("app_service")


class AppService:
    """Coordinates scanning, preview, organization, persistence, analytics, and exports."""

    def __init__(
        self,
        json_manager: JSONManager | None = None,
        csv_manager: CSVManager | None = None,
        history_manager: HistoryManager | None = None,
    ) -> None:
        self.json_manager = json_manager or JSONManager()
        self.csv_manager = csv_manager or CSVManager()
        self.history_manager = history_manager or HistoryManager()

        self.settings: Dict[str, Any] = self.json_manager.load_settings()
        self.records: List[Dict[str, Any]] = self.json_manager.load_records()
        self.csv_manager.ensure_log_file()

        self.rules_manager = CustomRulesManager(self.settings)
        self.scanner = FileScanner()
        self.duplicate_checker = DuplicateChecker()
        self.organizer = FileOrganizer()
        self.search_engine = FileSearchEngine()
        self.stats_engine = StatisticsEngine()
        self.export_manager = ReportExportManager()

        self.last_scan: Optional[ScanResult] = None
        self.last_preview: Optional[PreviewSummary] = None
        self.last_directory: str = ""

    def get_classifier(self) -> FileClassifier:
        """Build a FileClassifier reflecting the latest custom rules and folder names."""
        return FileClassifier(
            custom_categories=self.rules_manager.settings.get("custom_categories"),
            category_folder_names=self.rules_manager.settings.get("category_folder_names"),
        )

    def scan_directory(
        self,
        directory_path: str,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Tuple[ScanResult, PreviewSummary]:
        """Scan a directory and immediately build a non-destructive preview."""
        include_sub = bool(self.rules_manager.settings.get("include_subfolders", False))
        include_hidden = bool(self.rules_manager.settings.get("include_hidden_files", False))
        conflict_policy = str(self.rules_manager.settings.get("conflict_policy", "skip"))
        check_sha256 = bool(self.rules_manager.settings.get("check_sha256_duplicates", True))

        scan_result = self.scanner.scan(
            directory_path=directory_path,
            include_subfolders=include_sub,
            include_hidden=include_hidden,
            progress_callback=progress_callback,
        )
        classifier = self.get_classifier()
        preview_engine = PreviewEngine(classifier=classifier)
        preview = preview_engine.generate_preview(
            scan_result,
            conflict_policy=conflict_policy,
            check_sha256=check_sha256,
        )

        self.last_scan = scan_result
        self.last_preview = preview
        self.last_directory = scan_result.target_directory

        # Log scan activities to CSV
        ts = now_iso()
        csv_rows = [
            [ts, "SCAN", item.file_name, item.category, "Success"]
            for item in preview.items
        ]
        self.csv_manager.log_activities(csv_rows)

        return scan_result, preview

    def refresh_preview(self) -> Optional[PreviewSummary]:
        """Re-generate preview from the last scan using current settings."""
        if not self.last_scan:
            return None
        classifier = self.get_classifier()
        preview_engine = PreviewEngine(classifier=classifier)
        self.last_preview = preview_engine.generate_preview(
            self.last_scan,
            conflict_policy=str(self.rules_manager.settings.get("conflict_policy", "skip")),
            check_sha256=bool(self.rules_manager.settings.get("check_sha256_duplicates", True)),
        )
        return self.last_preview

    def execute_organization(
        self,
        confirmed: bool,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> OrganizationResult:
        """Execute organization for the current preview after explicit confirmation."""
        if not self.last_preview:
            raise ValueError("No preview available. Please scan a directory first.")
        result = self.organizer.organize(
            self.last_preview, confirmed=confirmed, progress_callback=progress_callback
        )

        # Persist records to file_records.json
        new_records = [
            {
                "file_name": r.file_name,
                "extension": r.extension,
                "category": r.category,
                "file_size": r.file_size,
                "source_path": r.source_path,
                "destination_path": r.destination_path,
                "status": r.status,
                "date_scanned": r.date_scanned,
            }
            for r in result.records
        ]
        self.records = self.json_manager.append_records(new_records)

        # Persist activity_log.csv
        ts = result.timestamp
        csv_rows = [
            [
                ts,
                "MOVE" if r.status == "Organized" else r.status.upper(),
                r.file_name,
                r.category,
                "Success" if r.status == "Organized" else r.status,
            ]
            for r in result.records
        ]
        self.csv_manager.log_activities(csv_rows)

        # Persist organization_history.json
        self.history_manager.add_operation(
            {
                "operation_id": result.operation_id,
                "timestamp": result.timestamp,
                "target_directory": result.target_directory,
                "total_attempted": result.total_attempted,
                "organized_count": result.organized_count,
                "skipped_count": result.skipped_count,
                "failed_count": result.failed_count,
                "movements": result.movements,
                "undone": False,
            }
        )
        return result

    def undo_last_organization(self) -> Dict[str, Any]:
        """Safely undo the most recent undoable organization batch."""
        last_op = self.history_manager.get_last_undoable_operation()
        if not last_op:
            return {
                "success": False,
                "message": "No undoable organization operation found.",
                "restored_count": 0,
                "skipped_count": 0,
                "failed_count": 0,
            }

        summary = self.organizer.undo_movements(last_op.get("movements", []))
        self.history_manager.mark_undone(last_op["operation_id"])
        self.csv_manager.log_activity(
            "UNDO",
            last_op["operation_id"],
            "System",
            f"Restored {summary['restored_count']}",
        )
        summary["success"] = True
        summary["operation_id"] = last_op["operation_id"]
        return summary

    def save_settings(self) -> bool:
        """Persist current rules and preferences to settings.json."""
        self.settings = self.rules_manager.settings
        return self.json_manager.save_settings(self.settings)

    def restore_default_settings(self) -> Dict[str, Any]:
        """Reset settings to defaults and save."""
        defaults = self.rules_manager.restore_defaults()
        self.save_settings()
        return defaults

    def get_metrics(self) -> Dict[str, Any]:
        """Return computed executive analytics from persisted records."""
        return self.stats_engine.compute_metrics(self.records)

    def search_records(
        self,
        query: str = "",
        extension: str = "",
        category: str = "All",
        status: str = "All",
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        sort_by: str = "file_name",
        descending: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search and filter persisted records."""
        return self.search_engine.search_and_filter(
            self.records,
            query=query,
            extension=extension,
            category=category,
            status=status,
            min_size=min_size,
            max_size=max_size,
            sort_by=sort_by,
            descending=descending,
        )

    def import_csv_records(self, csv_path: str) -> int:
        """Bulk import file records from a CSV file and persist them."""
        imported = self.csv_manager.import_records_from_csv(Path(csv_path))
        before = len(self.records)
        self.records = self.json_manager.append_records(imported)
        added = len(self.records) - before
        self.csv_manager.log_activity("IMPORT_CSV", Path(csv_path).name, "System", f"Added {added}")
        return added

    def export_report(self, fmt: str, destination: str | None = None) -> Path:
        """Export a report using current records, metrics, and history."""
        metrics = self.get_metrics()
        history = self.history_manager.load_history()
        out_path = self.export_manager.export_report(
            fmt=fmt,
            records=self.records,
            metrics=metrics,
            history=history,
            source_directory=self.last_directory or "All Persisted Records",
            destination=destination,
        )
        self.csv_manager.log_activity("EXPORT", out_path.name, "Report", "Success")
        return out_path
