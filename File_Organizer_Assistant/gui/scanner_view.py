"""File Scanner view with folder browser, background scanning, and live progress."""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Dict

from config.settings import BASE_DIR
from core.app_service import AppService
from gui.components import create_action_button, create_scrolled_treeview
from utils.file_utils import format_size


class ScannerView(tk.Frame):
    """Allows selecting a folder, scanning files safely, and viewing scan results."""

    def __init__(
        self,
        parent: tk.Misc,
        service: AppService,
        navigate: Callable[[str], None],
        palette: Dict[str, str],
    ) -> None:
        super().__init__(parent, bg=palette["bg"])
        self.service = service
        self.navigate = navigate
        self.palette = palette
        self.path_var = tk.StringVar()

        top = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        top.pack(fill="x", pady=(0, 12))

        tk.Label(
            top,
            text="File Scanner",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            top,
            text="Select a directory to scan. Scanning is read-only and never modifies files.",
            bg=palette["card"],
            fg=palette["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(2, 10))

        row = tk.Frame(top, bg=palette["card"])
        row.pack(fill="x")

        self.entry = tk.Entry(
            row,
            textvariable=self.path_var,
            bg=palette["input_bg"],
            fg=palette["text"],
            insertbackground=palette["text"],
            relief="flat",
            font=("Segoe UI", 10),
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        create_action_button(row, "Browse...", self._browse_folder, palette).pack(side="left", padx=(0, 6))
        create_action_button(row, "Demo Folder", self._create_and_select_demo, palette).pack(
            side="left", padx=(0, 6)
        )
        self.scan_btn = create_action_button(
            row, "Scan Directory", self._start_scan, palette, "success"
        )
        self.scan_btn.pack(side="left")

        prog_row = tk.Frame(top, bg=palette["card"])
        prog_row.pack(fill="x", pady=(10, 0))
        self.progress = ttk.Progressbar(
            prog_row, mode="indeterminate", style="Blue.Horizontal.TProgressbar"
        )
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.status_lbl = tk.Label(
            prog_row, text="Ready", bg=palette["card"], fg=palette["muted"], font=("Segoe UI", 9)
        )
        self.status_lbl.pack(side="left")

        # Results table
        table_card = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        table_card.pack(fill="both", expand=True)

        bar = tk.Frame(table_card, bg=palette["card"])
        bar.pack(fill="x", pady=(0, 8))
        self.summary_lbl = tk.Label(
            bar,
            text="No folder scanned yet.",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 10, "bold"),
        )
        self.summary_lbl.pack(side="left")
        create_action_button(
            bar, "Go to Preview ->", lambda: self.navigate("preview"), palette
        ).pack(side="right")

        container, self.tree = create_scrolled_treeview(
            table_card,
            [
                ("file_name", "File Name", 210),
                ("extension", "Ext", 80),
                ("category", "Category", 120),
                ("size", "Size", 95),
                ("modified", "Modified Date", 145),
                ("path", "Source Path", 300),
            ],
        )
        container.pack(fill="both", expand=True)

    def _browse_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select Folder to Scan")
        if folder:
            self.path_var.set(folder)

    def _create_and_select_demo(self) -> None:
        from cli import TerminalCLI

        TerminalCLI._create_demo_folder()
        self.path_var.set(str(BASE_DIR / "sample_test_folder"))

    def _start_scan(self) -> None:
        target = self.path_var.get().strip()
        if not target:
            messagebox.showwarning("Input Required", "Please select or enter a directory path.")
            return

        self.scan_btn.config(state="disabled")
        self.progress.start(12)
        self.status_lbl.config(text="Scanning...")

        def worker() -> None:
            try:
                scan_res, preview = self.service.scan_directory(
                    target,
                    progress_callback=lambda cnt, fname: self.after(
                        0, lambda c=cnt, n=fname: self.status_lbl.config(text=f"Scanned {c}: {n[:24]}")
                    ),
                )
                self.after(0, lambda: self._on_scan_success(scan_res, preview))
            except Exception as exc:
                self.after(0, lambda err=str(exc): self._on_scan_error(err))

        threading.Thread(target=worker, daemon=True).start()

    def _on_scan_success(self, scan_res, preview) -> None:
        self.progress.stop()
        self.scan_btn.config(state="normal")
        self.status_lbl.config(text=f"Done ({len(scan_res.files)} files)")
        self.summary_lbl.config(
            text=(
                f"Scanned: {len(scan_res.files)} files  |  "
                f"Total Size: {format_size(scan_res.total_size)}  |  "
                f"Errors: {len(scan_res.errors)}"
            )
        )
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in preview.items:
            self.tree.insert(
                "",
                "end",
                values=(
                    item.file_name,
                    item.extension or "(none)",
                    item.category,
                    item.size_formatted,
                    item.modified_date,
                    item.source_path,
                ),
            )

    def _on_scan_error(self, error_msg: str) -> None:
        self.progress.stop()
        self.scan_btn.config(state="normal")
        self.status_lbl.config(text="Error")
        messagebox.showerror("Scan Failed", error_msg)

    def refresh(self) -> None:
        """Refresh view if a scan already exists."""
        if self.service.last_scan and self.service.last_preview:
            self._on_scan_success(self.service.last_scan, self.service.last_preview)
