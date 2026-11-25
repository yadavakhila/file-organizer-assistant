"""Organization History & Safe Undo view."""

import tkinter as tk
from tkinter import messagebox
from typing import Dict

from core.app_service import AppService
from gui.components import create_action_button, create_scrolled_treeview


class HistoryView(tk.Frame):
    """Displays past organization operations and allows safely undoing the last batch."""

    def __init__(self, parent: tk.Misc, service: AppService, palette: Dict[str, str]) -> None:
        super().__init__(parent, bg=palette["bg"])
        self.service = service
        self.palette = palette

        top = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=16,
            pady=12,
        )
        top.pack(fill="x", pady=(0, 12))

        tk.Label(
            top,
            text="Organization History & Safe Undo",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left")

        create_action_button(
            top, "Undo Last Organization", self._undo_last, palette, "warning"
        ).pack(side="right")

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
                ("op_id", "Operation ID", 110),
                ("timestamp", "Timestamp", 150),
                ("directory", "Target Directory", 280),
                ("organized", "Organized", 90),
                ("skipped", "Skipped", 80),
                ("failed", "Failed", 70),
                ("undone", "Undone", 80),
            ],
        )
        container.pack(fill="both", expand=True)

    def refresh(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)
        history = self.service.history_manager.load_history()
        for h in reversed(history):
            self.tree.insert(
                "",
                "end",
                values=(
                    h.get("operation_id", ""),
                    h.get("timestamp", ""),
                    h.get("target_directory", ""),
                    h.get("organized_count", 0),
                    h.get("skipped_count", 0),
                    h.get("failed_count", 0),
                    "Yes" if h.get("undone") else "No",
                ),
            )

    def _undo_last(self) -> None:
        if not messagebox.askyesno(
            "Confirm Safe Undo",
            "Restore files from the most recent organization batch?\n"
            "Existing files will NEVER be overwritten.",
        ):
            return
        res = self.service.undo_last_organization()
        self.refresh()
        if res.get("success"):
            messagebox.showinfo(
                "Undo Complete",
                f"Operation: {res.get('operation_id')}\n"
                f"Restored: {res.get('restored_count')}\n"
                f"Skipped: {res.get('skipped_count')}\n"
                f"Failed: {res.get('failed_count')}",
            )
        else:
            messagebox.showinfo("Undo Info", str(res.get("message", "Nothing to undo.")))
