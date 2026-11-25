"""Interactive menu-driven Terminal CLI for File Organizer Assistant."""

from pathlib import Path
from typing import Optional

from config.settings import APP_NAME, APP_VERSION, BASE_DIR, PROJECT_CODE
from core.app_service import AppService
from utils.file_utils import format_size
from utils.validators import validate_confirmation


class TerminalCLI:
    """Menu-driven terminal interface using the shared AppService."""

    def __init__(self, service: Optional[AppService] = None) -> None:
        self.service = service or AppService()

    def run(self) -> None:
        """Start the interactive terminal loop."""
        self._print_banner()
        while True:
            self._print_menu()
            choice = input("\nSelect an option [0-10]: ").strip()

            if choice == "1":
                self._show_dashboard()
            elif choice == "2":
                self._scan_and_preview()
            elif choice == "3":
                self._review_and_organize()
            elif choice == "4":
                self._search_and_filter()
            elif choice == "5":
                self._show_analytics()
            elif choice == "6":
                self._manage_settings()
            elif choice == "7":
                self._history_and_undo()
            elif choice == "8":
                self._reports_and_import()
            elif choice == "9":
                self._create_demo_folder()
            elif choice == "10":
                self._launch_gui_from_cli()
            elif choice == "0":
                print("\nThank you for using File Organizer Assistant. Goodbye!")
                break
            else:
                print("\n[!] Invalid option. Please enter a number between 0 and 10.")

    @staticmethod
    def _print_banner() -> None:
        print("=" * 72)
        print(f"  {APP_NAME} v{APP_VERSION}  |  {PROJECT_CODE}")
        print("  Interactive Terminal Interface (Local-First & Non-Destructive Preview)")
        print("=" * 72)

    @staticmethod
    def _print_menu() -> None:
        print("\n--- MAIN MENU ---")
        print("  1. Dashboard & Executive Summary")
        print("  2. Scan Folder & Generate Preview")
        print("  3. Review Preview & Organize Files")
        print("  4. Search & Filter File Records")
        print("  5. Analytics & Category Breakdown")
        print("  6. Custom Rules & Settings")
        print("  7. Organization History & Undo Last Batch")
        print("  8. Export Reports (CSV / JSON / MD / TXT) & Bulk CSV Import")
        print("  9. Generate Safe Demo Test Folder")
        print(" 10. Launch Tkinter Graphical Interface")
        print("  0. Exit")

    def _show_dashboard(self) -> None:
        metrics = self.service.get_metrics()
        recent_logs = self.service.csv_manager.load_activities(limit=5)
        print("\n=== DASHBOARD ===")
        print(f"  Total Records Scanned : {metrics['total_files']}")
        print(f"  Total Organized       : {metrics['organized_files']}")
        print(f"  Total Skipped         : {metrics['skipped_files']}")
        print(f"  Total Failed          : {metrics['failed_files']}")
        print(f"  Success Rate          : {metrics['success_rate']}%")
        print(f"  Total Storage         : {metrics['total_storage_formatted']}")
        print(f"  Supported Categories  : {len(self.service.get_classifier().get_all_categories())}")
        print("\n  Recent Activity:")
        if not recent_logs:
            print("    (No recent activity logged yet)")
        else:
            for row in reversed(recent_logs):
                print(
                    f"    - [{row.get('timestamp', '')}] {row.get('action', '')}: "
                    f"{row.get('file_name', '')} ({row.get('category', '')}) -> {row.get('status', '')}"
                )

    def _scan_and_preview(self) -> None:
        print("\n=== SCAN FOLDER & PREVIEW ===")
        raw_path = input("Enter directory path to scan (or 'cancel'): ").strip()
        if raw_path.lower() == "cancel":
            print("Scan cancelled.")
            return

        try:
            scan_res, preview = self.service.scan_directory(
                raw_path,
                progress_callback=lambda count, name: print(
                    f"\r  Scanning... {count} files ({name[:30]})", end="", flush=True
                ),
            )
            print()
        except ValueError as exc:
            print(f"\n[!] Validation Error: {exc}")
            return

        print(f"\nScan complete for: {scan_res.target_directory}")
        print(f"  Files found    : {preview.total_scanned}")
        print(f"  Ready to move  : {preview.ready_to_move}")
        print(f"  Conflicts      : {preview.conflicts_count}")
        print(f"  Will be skipped: {preview.skipped_count}")
        print(f"  Total size     : {format_size(preview.total_size)}")
        if scan_res.errors:
            print(f"  Scan errors    : {len(scan_res.errors)}")

        self._display_preview_table()
        if preview.ready_to_move > 0:
            confirm = input("\nProceed to organize these files now? (yes/no): ")
            if validate_confirmation(confirm):
                self._execute_confirmed_organization()
            else:
                print("Organization cancelled. No files were modified.")

    def _review_and_organize(self) -> None:
        preview = self.service.refresh_preview()
        if not preview:
            print("\n[!] No active scan/preview. Use Option 2 to scan a folder first.")
            return
        self._display_preview_table()
        if preview.ready_to_move == 0:
            print("\nNothing to move (all files already organized or skipped).")
            return
        confirm = input("\nConfirm organization? Type 'yes' to move files: ")
        if validate_confirmation(confirm):
            self._execute_confirmed_organization()
        else:
            print("Cancelled. No files were moved.")

    def _display_preview_table(self) -> None:
        preview = self.service.last_preview
        if not preview or not preview.items:
            print("\n  (No files in preview)")
            return
        print("\n  PREVIEW (No files have been moved yet):")
        print(f"  {'File Name':<26} {'Ext':<8} {'Category':<14} {'Action':<8} {'Conflict Status'}")
        print("  " + "-" * 80)
        for item in preview.items[:40]:
            print(
                f"  {item.file_name[:25]:<26} {item.extension[:7]:<8} "
                f"{item.category[:13]:<14} {item.action:<8} {item.conflict_status}"
            )
        if len(preview.items) > 40:
            print(f"  ... and {len(preview.items) - 40} more items.")

    def _execute_confirmed_organization(self) -> None:
        result = self.service.execute_organization(
            confirmed=True,
            progress_callback=lambda idx, total, name: print(
                f"\r  Organizing {idx}/{total}: {name[:30]}", end="", flush=True
            ),
        )
        print()
        print("\n=== ORGANIZATION COMPLETE ===")
        print(f"  Operation ID : {result.operation_id}")
        print(f"  Organized    : {result.organized_count}")
        print(f"  Skipped      : {result.skipped_count}")
        print(f"  Failed       : {result.failed_count}")

    def _search_and_filter(self) -> None:
        print("\n=== SEARCH & FILTER RECORDS ===")
        query = input("Filename contains (leave blank for all): ").strip()
        ext = input("Extension filter e.g. .pdf (leave blank for all): ").strip()
        cat = input("Category filter (leave blank for All): ").strip() or "All"
        status = input("Status filter [Organized/Skipped/Failed/All]: ").strip() or "All"
        sort_by = input("Sort by [file_name/file_size/date] (default file_name): ").strip() or "file_name"

        results = self.service.search_records(
            query=query, extension=ext, category=cat, status=status, sort_by=sort_by
        )
        print(f"\nFound {len(results)} matching record(s):")
        print(f"  {'File Name':<28} {'Ext':<8} {'Category':<14} {'Size':<10} {'Status':<10} {'Date'}")
        print("  " + "-" * 84)
        for rec in results[:40]:
            print(
                f"  {str(rec.get('file_name', ''))[:27]:<28} "
                f"{str(rec.get('extension', ''))[:7]:<8} "
                f"{str(rec.get('category', ''))[:13]:<14} "
                f"{format_size(int(rec.get('file_size', 0))):<10} "
                f"{str(rec.get('status', ''))[:9]:<10} "
                f"{rec.get('date_scanned', '')}"
            )
        if len(results) > 40:
            print(f"  ... showing first 40 of {len(results)} results.")

    def _show_analytics(self) -> None:
        m = self.service.get_metrics()
        print("\n=== ANALYTICS & EXECUTIVE SUMMARY ===")
        print(f"  Total Files       : {m['total_files']}")
        print(f"  Organized         : {m['organized_files']}")
        print(f"  Skipped           : {m['skipped_files']}")
        print(f"  Failed            : {m['failed_files']}")
        print(f"  Success Rate      : {m['success_rate']}%")
        print(f"  Total Storage     : {m['total_storage_formatted']}")
        print(f"  Average File Size : {m['average_size_formatted']}")
        print(f"  Top Extension     : {m['most_common_extension']}")
        print("\n  Category Breakdown:")
        storage_map = m["storage_by_category"]
        for cat, count in m["category_counts"].items():
            print(f"    {cat:<16} : {count:>4} files  ({format_size(storage_map.get(cat, 0))})")

    def _manage_settings(self) -> None:
        while True:
            s = self.service.rules_manager.settings
            print("\n=== CUSTOM RULES & SETTINGS ===")
            print(f"  1. Include Subfolders   : {s.get('include_subfolders')}")
            print(f"  2. Include Hidden Files : {s.get('include_hidden_files')}")
            print(f"  3. Conflict Policy      : {s.get('conflict_policy')}")
            print(f"  4. SHA-256 Duplicate Chk: {s.get('check_sha256_duplicates')}")
            print("  5. Add Custom Extension to Category")
            print("  6. Create Custom Category")
            print("  7. Rename Category Destination Folder")
            print("  8. Restore Default Settings")
            print("  0. Back to Main Menu")
            sub = input("Select option: ").strip()

            if sub == "1":
                self.service.rules_manager.set_preference(
                    "include_subfolders", not s.get("include_subfolders", False)
                )
                self.service.save_settings()
            elif sub == "2":
                self.service.rules_manager.set_preference(
                    "include_hidden_files", not s.get("include_hidden_files", False)
                )
                self.service.save_settings()
            elif sub == "3":
                new_pol = "rename" if s.get("conflict_policy") == "skip" else "skip"
                self.service.rules_manager.set_preference("conflict_policy", new_pol)
                self.service.save_settings()
            elif sub == "4":
                self.service.rules_manager.set_preference(
                    "check_sha256_duplicates", not s.get("check_sha256_duplicates", True)
                )
                self.service.save_settings()
            elif sub == "5":
                cat = input("Category name: ").strip()
                ext = input("Extension (e.g. .log): ").strip()
                ok, msg = self.service.rules_manager.add_custom_extension(cat, ext)
                print(f"  {msg}")
                if ok:
                    self.service.save_settings()
            elif sub == "6":
                cat = input("New category name: ").strip()
                exts_raw = input("Comma-separated extensions (e.g. .psd,.ai): ").strip()
                exts = [e.strip() for e in exts_raw.split(",") if e.strip()]
                ok, msg = self.service.rules_manager.create_custom_category(cat, exts)
                print(f"  {msg}")
                if ok:
                    self.service.save_settings()
            elif sub == "7":
                cat = input("Existing category name: ").strip()
                folder = input("New destination folder name: ").strip()
                ok, msg = self.service.rules_manager.rename_category_folder(cat, folder)
                print(f"  {msg}")
                if ok:
                    self.service.save_settings()
            elif sub == "8":
                self.service.restore_default_settings()
                print("  Settings restored to defaults.")
            elif sub == "0":
                break
            else:
                print("  Invalid choice.")

    def _history_and_undo(self) -> None:
        history = self.service.history_manager.load_history()
        print("\n=== ORGANIZATION HISTORY ===")
        if not history:
            print("  No organization operations recorded yet.")
            return
        for h in history[-10:]:
            print(
                f"  [{h.get('operation_id')}] {h.get('timestamp')} | "
                f"Org={h.get('organized_count')} Skip={h.get('skipped_count')} "
                f"Fail={h.get('failed_count')} | Undone={h.get('undone')} | {h.get('target_directory')}"
            )
        ans = input("\nUndo the last undoable organization? (yes/no): ")
        if validate_confirmation(ans):
            res = self.service.undo_last_organization()
            if res.get("success"):
                print(
                    f"  Undo {res['operation_id']} complete: "
                    f"Restored={res['restored_count']}, Skipped={res['skipped_count']}, Failed={res['failed_count']}"
                )
            else:
                print(f"  {res.get('message')}")

    def _reports_and_import(self) -> None:
        print("\n=== REPORTS & BULK CSV IMPORT ===")
        print("  1. Export CSV Report")
        print("  2. Export JSON Report")
        print("  3. Export Markdown Report")
        print("  4. Export Plain-Text Audit Report")
        print("  5. Bulk Import Records from CSV")
        print("  0. Back")
        sub = input("Select option: ").strip()
        fmt_map = {"1": "csv", "2": "json", "3": "md", "4": "txt"}
        if sub in fmt_map:
            dest = input("Export directory or file path (blank for default exports/): ").strip() or None
            try:
                out = self.service.export_report(fmt_map[sub], destination=dest)
                print(f"  Report exported successfully to: {out}")
            except ValueError as exc:
                print(f"  [!] Export failed: {exc}")
        elif sub == "5":
            csv_path = input("Path to CSV file to import: ").strip()
            try:
                added = self.service.import_csv_records(csv_path)
                print(f"  Imported {added} new unique record(s).")
            except (FileNotFoundError, OSError) as exc:
                print(f"  [!] Import failed: {exc}")

    @staticmethod
    def _create_demo_folder() -> None:
        demo_dir = BASE_DIR / "sample_test_folder"
        demo_dir.mkdir(parents=True, exist_ok=True)
        sample_files = {
            "annual_report.pdf": "Sample PDF content",
            "meeting_notes.txt": "Project meeting notes",
            "vacation_photo.JPG": "JPEG binary placeholder",
            "logo_design.png": "PNG binary placeholder",
            "demo_video.mp4": "MP4 placeholder",
            "podcast_ep1.mp3": "MP3 audio placeholder",
            "backup_archive.zip": "ZIP archive placeholder",
            "main_script.py": "print('Hello File Organizer')\n",
            "styles.css": "body { background: #0f172a; }\n",
            "budget_2026.xlsx": "Spreadsheet placeholder",
            "sales_data.csv": "month,sales\nJan,100\nFeb,150\n",
            "installer_setup.exe": "Executable placeholder",
            "unknown_blob.xyz": "Unknown extension data",
            "README_old.doc": "Legacy doc placeholder",
        }
        for fname, content in sample_files.items():
            target = demo_dir / fname
            if not target.exists():
                target.write_text(content, encoding="utf-8")
        print(f"\nDemo test folder ready at: {demo_dir}")
        print("You can now scan this folder safely using Option 2!")

    def _launch_gui_from_cli(self) -> None:
        try:
            from gui.app import launch_gui
        except ImportError as exc:
            print(f"\n[!] Tkinter GUI unavailable: {exc}")
            return
        print("\nLaunching Tkinter GUI...")
        launch_gui(self.service)
