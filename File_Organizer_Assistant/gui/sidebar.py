"""Sidebar navigation component for File Organizer Assistant."""

import tkinter as tk
from typing import Callable, Dict, List, Tuple

from config.settings import APP_VERSION


NAV_ITEMS: List[Tuple[str, str]] = [
    ("dashboard", "Dashboard"),
    ("scanner", "File Scanner"),
    ("preview", "Preview & Organize"),
    ("classification", "Classification"),
    ("explorer", "File Explorer"),
    ("analytics", "Analytics"),
    ("history", "History & Undo"),
    ("settings", "Rules & Settings"),
    ("reports", "Reports & Export"),
    ("about", "About"),
]


class Sidebar(tk.Frame):
    """Left navigation rail with active item highlighting."""

    def __init__(
        self,
        parent: tk.Misc,
        on_select: Callable[[str], None],
        palette: Dict[str, str],
    ) -> None:
        super().__init__(parent, bg=palette["sidebar"], width=215)
        self.pack_propagate(False)
        self.on_select = on_select
        self.palette = palette
        self.buttons: Dict[str, tk.Button] = {}

        header = tk.Frame(self, bg=palette["sidebar"], padx=16, pady=18)
        header.pack(fill="x")
        tk.Label(
            header,
            text="File Organizer",
            bg=palette["sidebar"],
            fg="#FFFFFF",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text=f"Assistant v{APP_VERSION}",
            bg=palette["sidebar"],
            fg="#94A3B8",
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        tk.Frame(self, bg="#1E293B", height=1).pack(fill="x", padx=12, pady=(0, 8))

        for key, label in NAV_ITEMS:
            btn = tk.Button(
                self,
                text=f"  {label}",
                anchor="w",
                command=lambda k=key: self.on_select(k),
                bg=palette["sidebar"],
                fg="#CBD5E1",
                activebackground="#1E293B",
                activeforeground="#FFFFFF",
                relief="flat",
                bd=0,
                padx=16,
                pady=9,
                cursor="hand2",
                font=("Segoe UI", 10),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.buttons[key] = btn

    def set_active(self, active_key: str) -> None:
        """Highlight the currently active navigation button."""
        for key, btn in self.buttons.items():
            if key == active_key:
                btn.config(bg=self.palette["accent"], fg="#FFFFFF", font=("Segoe UI", 10, "bold"))
            else:
                btn.config(bg=self.palette["sidebar"], fg="#CBD5E1", font=("Segoe UI", 10))
