"""File Explorer view with search, multi-criteria filtering, sorting, and bulk CSV import."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict

from core.app_service import AppService
from gui.components import create_action_button, create_scrolled_treeview
from utils.file_utils import format_size


class ExplorerView(tk.Frame):
    """Search and filter persisted file records."""

    def __init__(self, parent: tk.Misc, service: AppService, palette: Dict[str, str]) -> None:
        super().__init__(parent, bg=palette["bg"])
        self.service = service
        self.palette = palette

        self.query_var = tk.StringVar()
        self.ext_var = tk.StringVar()
        self.cat_var = tk.StringVar(value="All")
        self.status_var = tk.StringVar(value="All")
        self.sort_var = tk.StringVar(value="file_name")

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
            text="File Explorer & Search",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        filters = tk.Frame(top, bg=palette["card"])
        filters.pack(fill="x")

        tk.Label(filters, text="Name:", bg=palette["card"], fg=palette["muted"]).pack(side="left")
        tk.Entry(
            filters,
            textvariable=self.query_var,
            bg=palette["input_bg"],
            fg=palette["text"],
            insertbackground=palette["text"],
            relief="flat",
            width=18,
        ).pack(side="left", padx=(4, 10), ipady=4)

        tk.Label(filters, text="Ext:", bg=palette["card"], fg=palette["muted"]).pack(side="left")
        tk.Entry(
            filters,
            textvariable=self.ext_var,
            bg=palette["input_bg"],
            fg=palette["text"],
            insertbackground=palette["text"],
            relief="flat",
            width=8,
        ).pack(side="left", padx=(4, 10), ipady=4)

        tk.Label(filters, text="Category:", bg=palette["card"], fg=palette["muted"]).pack(side="left")
        self.cat_combo = ttk.Combobox(filters, textvariable=self.cat_var, width=13, state="readonly")
        self.cat_combo.pack(side="left", padx=(4, 10))

        tk.Label(filters, text="Status:", bg=palette["card"], fg=palette["muted"]).pack(side="left")
        ttk.Combobox(
            filters,
            textvariable=self.status_var,
            values=["All", "Organized", "Skipped", "Failed", "Scanned"],
            width=11,
            state="readonly",
        ).pack(side="left", padx=(4, 10))

        tk.Label(filters, text="Sort:", bg=palette["card"], fg=palette["muted"]).pack(side="left")
        ttk.Combobox(
            filters,
            textvariable=self.sort_var,
            values=["file_name", "file_size", "date", "category", "status"],
            width=11,
            state="readonly",
        ).pack(side="left", padx=(4, 10))

        create_action_button(filters, "Apply", self.refresh, palette).pack(side="left", padx=(0, 6))
        create_action_button(filters, "Clear", self._clear_filters, palette, "warning").pack(
            side="left", padx=(0, 6)
        )
        create_action_button(filters, "Import CSV", self._import_csv, palette, "success").pack(side="right")

        table_card = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        table_card.pack(fill="both", expand=True)

        self.count_lbl = tk.Label(
            table_card, text="0 records", bg=palette["card"], fg=palette["muted"], font=("Segoe UI", 9)
        )
        self.count_lbl.pack(anchor="w", pady=(0, 6))

        container, self.tree = create_scrolled_treeview(
            table_card,
            [
                ("file_name", "File Name", 200),
                ("extension", "Ext", 70),
                ("category", "Category", 115),
                ("size", "Size", 90),
                ("status", "Status", 95),
                ("date", "Date", 100),
                ("destination", "Destination Path", 300),
            ],
        )
        container.pack(fill="both", expand=True)

    def _clear_filters(self) -> None:
        self.query_var.set("")
        self.ext_var.set("")
        self.cat_var.set("All")
        self.status_var.set("All")
        self.sort_var.set("file_name")
        self.refresh()

    def _import_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Select CSV File to Import", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            added = self.service.import_csv_records(path)
            self.refresh()
            messagebox.showinfo("CSV Import Complete", f"Imported {added} new unique record(s).")
        except Exception as exc:
            messagebox.showerror("CSV Import Failed", str(exc))

    def refresh(self) -> None:
        """Reload categories and filter persisted records."""
        cats = ["All"] + list(self.service.get_classifier().get_all_categories().keys())
        self.cat_combo["values"] = cats

        results = self.service.search_records(
            query=self.query_var.get(),
            extension=self.ext_var.get(),
            category=self.cat_var.get(),
            status=self.status_var.get(),
            sort_by=self.sort_var.get(),
        )
        self.count_lbl.config(text=f"Showing {len(results)} record(s)")
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in results:
            self.tree.insert(
                "",
                "end",
                values=(
                    rec.get("file_name", ""),
                    rec.get("extension", ""),
                    rec.get("category", ""),
                    format_size(int(rec.get("file_size", 0) or 0)),
                    rec.get("status", ""),
                    rec.get("date_scanned", ""),
                    rec.get("destination_path", ""),
                ),
            )
