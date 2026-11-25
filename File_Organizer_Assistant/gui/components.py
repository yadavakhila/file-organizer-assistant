"""Reusable Tkinter UI components and dark-navy / light theme palettes."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Tuple

DARK_THEME: Dict[str, str] = {
    "bg": "#0B1120",
    "sidebar": "#0F172A",
    "card": "#131C2E",
    "card_border": "#1E293B",
    "accent": "#3B82F6",
    "accent_hover": "#2563EB",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text": "#F8FAFC",
    "muted": "#94A3B8",
    "input_bg": "#1E293B",
    "table_bg": "#131C2E",
    "table_alt": "#182238",
}

LIGHT_THEME: Dict[str, str] = {
    "bg": "#F1F5F9",
    "sidebar": "#1E293B",
    "card": "#FFFFFF",
    "card_border": "#CBD5E1",
    "accent": "#2563EB",
    "accent_hover": "#1D4ED8",
    "success": "#059669",
    "warning": "#D97706",
    "danger": "#DC2626",
    "text": "#0F172A",
    "muted": "#475569",
    "input_bg": "#FFFFFF",
    "table_bg": "#FFFFFF",
    "table_alt": "#F8FAFC",
}


def get_palette(theme_name: str = "dark") -> Dict[str, str]:
    """Return color palette dictionary for the requested theme."""
    return LIGHT_THEME if theme_name == "light" else DARK_THEME


def configure_ttk_styles(root: tk.Misc, palette: Dict[str, str]) -> None:
    """Apply consistent ttk styling for Treeview, Notebook, Progressbar, and Combobox."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Treeview",
        background=palette["table_bg"],
        foreground=palette["text"],
        fieldbackground=palette["table_bg"],
        borderwidth=0,
        rowheight=26,
        font=("Segoe UI", 9),
    )
    style.configure(
        "Treeview.Heading",
        background=palette["card_border"],
        foreground=palette["text"],
        font=("Segoe UI", 9, "bold"),
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", palette["accent"])],
        foreground=[("selected", "#FFFFFF")],
    )
    style.configure(
        "Blue.Horizontal.TProgressbar",
        troughcolor=palette["input_bg"],
        background=palette["accent"],
        borderwidth=0,
    )


class StatCard(tk.Frame):
    """Dashboard metric card with title, primary value, and accent stripe."""

    def __init__(
        self,
        parent: tk.Misc,
        title: str,
        value: str,
        palette: Dict[str, str],
        accent_color: str | None = None,
    ) -> None:
        super().__init__(
            parent,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        stripe = tk.Frame(self, bg=accent_color or palette["accent"], width=4)
        stripe.pack(side="left", fill="y", padx=(0, 10))

        body = tk.Frame(self, bg=palette["card"])
        body.pack(side="left", fill="both", expand=True)

        self.title_lbl = tk.Label(
            body, text=title, bg=palette["card"], fg=palette["muted"], font=("Segoe UI", 9)
        )
        self.title_lbl.pack(anchor="w")

        self.value_lbl = tk.Label(
            body, text=value, bg=palette["card"], fg=palette["text"], font=("Segoe UI", 16, "bold")
        )
        self.value_lbl.pack(anchor="w", pady=(2, 0))

    def set_value(self, value: str) -> None:
        """Update displayed metric value."""
        self.value_lbl.config(text=value)


def create_action_button(
    parent: tk.Misc,
    text: str,
    command: Callable[[], None],
    palette: Dict[str, str],
    color_key: str = "accent",
) -> tk.Button:
    """Create a flat modern button."""
    bg = palette.get(color_key, palette["accent"])
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg="#FFFFFF",
        activebackground=palette["accent_hover"],
        activeforeground="#FFFFFF",
        relief="flat",
        bd=0,
        padx=14,
        pady=7,
        cursor="hand2",
        font=("Segoe UI", 9, "bold"),
    )
    return btn


def create_scrolled_treeview(
    parent: tk.Misc,
    columns: List[Tuple[str, str, int]],
) -> Tuple[tk.Frame, ttk.Treeview]:
    """Create a Treeview with vertical and horizontal scrollbars."""
    container = tk.Frame(parent)
    col_ids = [c[0] for c in columns]
    tree = ttk.Treeview(container, columns=col_ids, show="headings", selectmode="browse")

    for col_id, heading, width in columns:
        tree.heading(col_id, text=heading)
        tree.column(col_id, width=width, anchor="w", minwidth=60)

    vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)
    return container, tree
