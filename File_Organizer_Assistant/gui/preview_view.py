"""Preview & Organization view requiring explicit user confirmation before moving files."""

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Dict

from core.app_service import AppService
from gui.components import create_action_button, create_scrolled_treeview


class PreviewView(tk.Frame):
    """Non-destructive preview table with Confirm Organization, Refresh, and Cancel actions."""

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
            text="Preview & File Organization",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            top,
            text="Preview mode is 100% non-destructive. Files are moved only after you confirm.",
            bg=palette["card"],
            fg=palette["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(2, 10))

        controls = tk.Frame(top, bg=palette["card"])
        controls.pack(fill="x")

        self.summary_lbl = tk.Label(
            controls,
            text="No active preview. Scan a folder first.",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 10, "bold"),
        )
        self.summary_lbl.pack(side="left")

        btn_box = tk.Frame(controls, bg=palette["card"])
        btn_box.pack(side="right")
        create_action_button(btn_box, "Refresh Preview", self.refresh, palette).pack(
            side="left", padx=(0, 8)
        )
        create_action_button(
            btn_box, "Cancel", lambda: self.navigate("dashboard"), palette, "danger"
        ).pack(side="left", padx=(0, 8))
        self.confirm_btn = create_action_button(
            btn_box, "Confirm Organization", self._confirm_and_organize, palette, "success"
        )
        self.confirm_btn.pack(side="left")

        self.progress = ttk.Progressbar(
            top, mode="determinate", style="Blue.Horizontal.TProgressbar"
        )
        self.progress.pack(fill="x", pady=(10, 0))

        table_card = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        table_card.pack(fill="both", expand=True)

        container, self.tree = create_scrolled_treeview(
            table_card,
            [
                ("file_name", "File Name", 180),
                ("extension", "Ext", 70),
                ("category", "Category", 110),
                ("action", "Action", 70),
                ("conflict", "Conflict Status", 150),
                ("destination", "Proposed Destination", 320),
            ],
        )
        container.pack(fill="both", expand=True)

    def refresh(self) -> None:
        """Regenerate preview from last scan without modifying files."""
        preview = self.service.refresh_preview()
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not preview:
            self.summary_lbl.config(text="No active preview. Scan a folder first.")
            return

        self.summary_lbl.config(
            text=(
                f"Total: {preview.total_scanned}  |  Ready: {preview.ready_to_move}  |  "
                f"Conflicts: {preview.conflicts_count}  |  Skipped: {preview.skipped_count}"
            )
        )
        for item in preview.items:
            self.tree.insert(
                "",
                "end",
                values=(
                    item.file_name,
                    item.extension or "(none)",
                    item.category,
                    item.action,
                    item.conflict_status,
                    item.proposed_destination,
                ),
            )

    def _confirm_and_organize(self) -> None:
        preview = self.service.last_preview
        if not preview or preview.ready_to_move == 0:
            messagebox.showinfo("Nothing to Organize", "No files are ready to move in the current preview.")
            return

        approved = messagebox.askyesno(
            "Confirm File Organization",
            f"Move {preview.ready_to_move} file(s) into categorized folders inside:\n"
            f"{preview.target_directory}\n\n"
            f"({preview.skipped_count} file(s) will be safely skipped.)",
        )
        if not approved:
            return

        self.confirm_btn.config(state="disabled")
        self.progress["maximum"] = max(1, len(preview.items))
        self.progress["value"] = 0

        def worker() -> None:
            try:
                result = self.service.execute_organization(
                    confirmed=True,
                    progress_callback=lambda idx, total, _name: self.after(
                        0, lambda v=idx: self.progress.configure(value=v)
                    ),
                )
                self.after(0, lambda: self._on_done(result))
            except Exception as exc:
                self.after(0, lambda err=str(exc): self._on_error(err))

        threading.Thread(target=worker, daemon=True).start()

    def _on_done(self, result) -> None:
        self.confirm_btn.config(state="normal")
        self.refresh()
        messagebox.showinfo(
            "Organization Complete",
            f"Operation ID: {result.operation_id}\n"
            f"Organized: {result.organized_count}\n"
            f"Skipped: {result.skipped_count}\n"
            f"Failed: {result.failed_count}",
        )

    def _on_error(self, err: str) -> None:
        self.confirm_btn.config(state="normal")
        messagebox.showerror("Organization Error", err)
