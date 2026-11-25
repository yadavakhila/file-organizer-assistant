"""Reports Export, Classification Reference, and About views."""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict

from config.settings import APP_NAME, APP_VERSION, PROJECT_CODE
from core.app_service import AppService
from gui.components import create_action_button, create_scrolled_treeview


class ReportsView(tk.Frame):
    """Export reports in CSV, JSON, Markdown, and Plain-Text formats."""

    def __init__(self, parent: tk.Misc, service: AppService, palette: Dict[str, str]) -> None:
        super().__init__(parent, bg=palette["bg"])
        self.service = service
        self.palette = palette

        card = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=20,
            pady=18,
        )
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text="Reports & Audit Export",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            card,
            text="Generate evaluation-ready reports with executive summary, category totals, and history.",
            bg=palette["card"],
            fg=palette["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(3, 16))

        btn_grid = tk.Frame(card, bg=palette["card"])
        btn_grid.pack(anchor="w", pady=(0, 14))

        for label, fmt in [
            ("Export CSV Report", "csv"),
            ("Export JSON Report", "json"),
            ("Export Markdown (.md)", "md"),
            ("Export Plain-Text Audit (.txt)", "txt"),
        ]:
            create_action_button(
                btn_grid, label, lambda f=fmt: self._export(f), palette
            ).pack(side="left", padx=(0, 10))

        self.status_lbl = tk.Label(
            card, text="", bg=palette["card"], fg=palette["success"], font=("Segoe UI", 10)
        )
        self.status_lbl.pack(anchor="w", pady=(8, 0))

    def _export(self, fmt: str) -> None:
        dest = filedialog.asksaveasfilename(
            title=f"Save {fmt.upper()} Report",
            defaultextension=f".{fmt}",
            filetypes=[(f"{fmt.upper()} Files", f"*.{fmt}"), ("All Files", "*.*")],
        )
        if not dest:
            return
        try:
            out_path = self.service.export_report(fmt, destination=dest)
            self.status_lbl.config(text=f"Exported successfully to: {out_path}")
            messagebox.showinfo("Export Complete", f"Report saved to:\n{out_path}")
        except Exception as exc:
            messagebox.showerror("Export Failed", str(exc))

    def refresh(self) -> None:
        pass


class ClassificationView(tk.Frame):
    """Displays active classification categories, extensions, and custom folder names."""

    def __init__(self, parent: tk.Misc, service: AppService, palette: Dict[str, str]) -> None:
        super().__init__(parent, bg=palette["bg"])
        self.service = service
        self.palette = palette

        card = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text="Smart File Classification Rules",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        container, self.tree = create_scrolled_treeview(
            card,
            [
                ("category", "Category", 160),
                ("folder", "Destination Folder", 170),
                ("extensions", "Supported Extensions", 520),
            ],
        )
        container.pack(fill="both", expand=True)

    def refresh(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)
        classifier = self.service.get_classifier()
        for cat, exts in classifier.get_all_categories().items():
            folder = classifier.get_folder_name(cat)
            ext_str = ", ".join(exts) if exts else "(All unrecognized extensions)"
            self.tree.insert("", "end", values=(cat, folder, ext_str))


class AboutView(tk.Frame):
    """Displays academic project information and architecture details."""

    def __init__(self, parent: tk.Misc, palette: Dict[str, str]) -> None:
        super().__init__(parent, bg=palette["bg"])
        card = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=24,
            pady=22,
        )
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text=f"{APP_NAME} v{APP_VERSION}",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            card,
            text=PROJECT_CODE,
            bg=palette["card"],
            fg=palette["accent"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(2, 12))

        info = (
            "Domain: Digital Tools & Productivity\n"
            "Technology Stack: Python 3.10+, Tkinter/ttk, pathlib, shutil, json, csv, hashlib, Matplotlib\n\n"
            "Core Capabilities:\n"
            "• Safe directory scanning with symlink protection and permission error handling\n"
            "• Case-insensitive smart extension classification with custom categories\n"
            "• 100% non-destructive Preview Mode before any file movement\n"
            "• SHA-256 duplicate detection and zero-overwrite conflict handling\n"
            "• JSON & CSV persistence with corruption recovery and Safe Undo\n"
            "• Executive analytics, Matplotlib charts, and CSV/JSON/Markdown/TXT report exports\n"
            "• Dual interface: Mandatory Interactive Terminal CLI + Tkinter Desktop GUI"
        )
        tk.Label(
            card,
            text=info,
            bg=palette["card"],
            fg=palette["muted"],
            justify="left",
            font=("Segoe UI", 10),
        ).pack(anchor="w")

    def refresh(self) -> None:
        pass
