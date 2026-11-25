"""Export manager for generating CSV, JSON, Markdown, and plain-text audit reports."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from config.settings import APP_NAME, EXPORTS_DIR, PROJECT_CODE
from utils.date_utils import now_iso, timestamp_slug
from utils.file_utils import ensure_directory, format_size
from utils.validators import validate_export_path


class ReportExportManager:
    """Generates and exports professional reports in CSV, JSON, Markdown, and TXT formats."""

    def export_report(
        self,
        fmt: str,
        records: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        history: List[Dict[str, Any]],
        source_directory: str = "N/A",
        destination: str | None = None,
    ) -> Path:
        """Export a report in the requested format ('csv', 'json', 'md', 'txt')."""
        fmt_clean = fmt.strip().lower()
        if fmt_clean not in {"csv", "json", "md", "txt"}:
            raise ValueError(f"Unsupported report format: {fmt}")

        if destination:
            ok, msg, resolved = validate_export_path(destination)
            if not ok or resolved is None:
                raise ValueError(msg)
            out_path = resolved / f"report_{timestamp_slug()}.{fmt_clean}" if resolved.is_dir() else resolved
        else:
            ensure_directory(EXPORTS_DIR)
            out_path = EXPORTS_DIR / f"file_organizer_report_{timestamp_slug()}.{fmt_clean}"

        out_path.parent.mkdir(parents=True, exist_ok=True)

        if fmt_clean == "csv":
            self._export_csv(out_path, records, metrics, source_directory)
        elif fmt_clean == "json":
            self._export_json(out_path, records, metrics, history, source_directory)
        elif fmt_clean == "md":
            self._export_markdown(out_path, records, metrics, history, source_directory)
        else:
            self._export_txt(out_path, records, metrics, history, source_directory)

        return out_path

    def _export_csv(
        self,
        out_path: Path,
        records: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        source_directory: str,
    ) -> None:
        with out_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["Application", APP_NAME])
            writer.writerow(["Generated At", now_iso()])
            writer.writerow(["Source Directory", source_directory])
            writer.writerow(["Total Scanned", metrics.get("total_files", 0)])
            writer.writerow(["Files Organized", metrics.get("organized_files", 0)])
            writer.writerow(["Files Skipped", metrics.get("skipped_files", 0)])
            writer.writerow(["Failed Operations", metrics.get("failed_files", 0)])
            writer.writerow(["Total Storage", metrics.get("total_storage_formatted", "0 B")])
            writer.writerow([])
            writer.writerow(["Category", "File Count", "Storage (Bytes)"])
            storage_map = metrics.get("storage_by_category", {})
            for cat, count in metrics.get("category_counts", {}).items():
                writer.writerow([cat, count, storage_map.get(cat, 0)])
            writer.writerow([])
            writer.writerow(
                [
                    "file_name",
                    "extension",
                    "category",
                    "file_size",
                    "source_path",
                    "destination_path",
                    "status",
                    "date_scanned",
                ]
            )
            for rec in records:
                writer.writerow(
                    [
                        rec.get("file_name", ""),
                        rec.get("extension", ""),
                        rec.get("category", ""),
                        rec.get("file_size", 0),
                        rec.get("source_path", ""),
                        rec.get("destination_path", ""),
                        rec.get("status", ""),
                        rec.get("date_scanned", ""),
                    ]
                )

    def _export_json(
        self,
        out_path: Path,
        records: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        history: List[Dict[str, Any]],
        source_directory: str,
    ) -> None:
        payload = {
            "application": APP_NAME,
            "project": PROJECT_CODE,
            "generated_at": now_iso(),
            "source_directory": source_directory,
            "summary": metrics,
            "operation_history": history,
            "records": records,
        }
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _export_markdown(
        self,
        out_path: Path,
        records: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        history: List[Dict[str, Any]],
        source_directory: str,
    ) -> None:
        lines = [
            f"# {APP_NAME} — Audit Report",
            "",
            f"- **Project:** {PROJECT_CODE}",
            f"- **Generated At:** {now_iso()}",
            f"- **Source Directory:** `{source_directory}`",
            "",
            "## Executive Summary",
            "",
            "| Metric | Value |",
            "|---|---|",
            f"| Total Files Scanned | {metrics.get('total_files', 0)} |",
            f"| Files Organized | {metrics.get('organized_files', 0)} |",
            f"| Files Skipped | {metrics.get('skipped_files', 0)} |",
            f"| Failed Operations | {metrics.get('failed_files', 0)} |",
            f"| Organization Success Rate | {metrics.get('success_rate', 0.0)}% |",
            f"| Total Storage Processed | {metrics.get('total_storage_formatted', '0 B')} |",
            f"| Average File Size | {metrics.get('average_size_formatted', '0 B')} |",
            f"| Most Common Extension | `{metrics.get('most_common_extension', 'N/A')}` |",
            "",
            "## Category Breakdown",
            "",
            "| Category | File Count | Storage |",
            "|---|---|---|",
        ]
        storage_map = metrics.get("storage_by_category", {})
        for cat, count in metrics.get("category_counts", {}).items():
            lines.append(f"| {cat} | {count} | {format_size(storage_map.get(cat, 0))} |")

        lines.extend(["", "## Recent Operation History", ""])
        if history:
            lines.append("| Operation ID | Timestamp | Directory | Organized | Skipped | Failed | Undone |")
            lines.append("|---|---|---|---|---|---|---|")
            for h in history[-10:]:
                lines.append(
                    f"| {h.get('operation_id', '')} | {h.get('timestamp', '')} | "
                    f"`{h.get('target_directory', '')}` | {h.get('organized_count', 0)} | "
                    f"{h.get('skipped_count', 0)} | {h.get('failed_count', 0)} | "
                    f"{'Yes' if h.get('undone') else 'No'} |"
                )
        else:
            lines.append("_No organization operations recorded yet._")

        lines.extend(["", f"_Total file records included: {len(records)}_", ""])
        out_path.write_text("\n".join(lines), encoding="utf-8")

    def _export_txt(
        self,
        out_path: Path,
        records: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        history: List[Dict[str, Any]],
        source_directory: str,
    ) -> None:
        sep = "=" * 70
        lines = [
            sep,
            f"{APP_NAME} - PLAIN TEXT AUDIT REPORT",
            sep,
            f"Project          : {PROJECT_CODE}",
            f"Generated At     : {now_iso()}",
            f"Source Directory : {source_directory}",
            "",
            "EXECUTIVE SUMMARY",
            "-" * 70,
            f"Total Files Scanned      : {metrics.get('total_files', 0)}",
            f"Files Organized          : {metrics.get('organized_files', 0)}",
            f"Files Skipped            : {metrics.get('skipped_files', 0)}",
            f"Failed Operations        : {metrics.get('failed_files', 0)}",
            f"Success Rate             : {metrics.get('success_rate', 0.0)}%",
            f"Total Storage Processed  : {metrics.get('total_storage_formatted', '0 B')}",
            f"Average File Size        : {metrics.get('average_size_formatted', '0 B')}",
            f"Most Common Extension    : {metrics.get('most_common_extension', 'N/A')}",
            "",
            "CATEGORY BREAKDOWN",
            "-" * 70,
        ]
        storage_map = metrics.get("storage_by_category", {})
        for cat, count in metrics.get("category_counts", {}).items():
            lines.append(f"  {cat:<18} : {count:>5} files  ({format_size(storage_map.get(cat, 0))})")

        lines.extend(["", "OPERATION HISTORY (LAST 10)", "-" * 70])
        if history:
            for h in history[-10:]:
                lines.append(
                    f"  [{h.get('operation_id')}] {h.get('timestamp')} | "
                    f"Org={h.get('organized_count', 0)} Skip={h.get('skipped_count', 0)} "
                    f"Fail={h.get('failed_count', 0)} | Undone={h.get('undone', False)}"
                )
        else:
            lines.append("  No operations recorded.")

        lines.extend(["", f"Total Persisted Records: {len(records)}", sep])
        out_path.write_text("\n".join(lines), encoding="utf-8")
