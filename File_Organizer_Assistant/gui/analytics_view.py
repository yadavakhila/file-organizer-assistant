"""Analytics & Executive Summary view with embedded Matplotlib charts."""

import tkinter as tk
from typing import Dict

from analytics.charts import (
    MATPLOTLIB_AVAILABLE,
    build_category_bar_figure,
    build_category_pie_figure,
    build_storage_bar_figure,
)
from core.app_service import AppService
from gui.components import StatCard

if MATPLOTLIB_AVAILABLE:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AnalyticsView(tk.Frame):
    """Displays executive metrics and visual Matplotlib charts."""

    def __init__(self, parent: tk.Misc, service: AppService, palette: Dict[str, str]) -> None:
        super().__init__(parent, bg=palette["bg"])
        self.service = service
        self.palette = palette
        self.dark_mode = self.service.rules_manager.settings.get("theme", "dark") == "dark"

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
            text="Analytics & Executive Summary",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")

        kpi_row = tk.Frame(self, bg=palette["bg"])
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)

        self.c_total = StatCard(kpi_row, "Total Files", "0", palette)
        self.c_avg = StatCard(kpi_row, "Average File Size", "0 B", palette)
        self.c_rate = StatCard(kpi_row, "Success Rate", "0.0%", palette, palette["success"])
        self.c_ext = StatCard(kpi_row, "Most Common Ext", "N/A", palette)

        self.c_total.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.c_avg.grid(row=0, column=1, sticky="nsew", padx=4)
        self.c_rate.grid(row=0, column=2, sticky="nsew", padx=4)
        self.c_ext.grid(row=0, column=3, sticky="nsew", padx=(8, 0))

        self.charts_frame = tk.Frame(self, bg=palette["bg"])
        self.charts_frame.pack(fill="both", expand=True)

    def refresh(self) -> None:
        """Recompute metrics and redraw charts."""
        self.dark_mode = self.service.rules_manager.settings.get("theme", "dark") == "dark"
        m = self.service.get_metrics()
        self.c_total.set_value(str(m["total_files"]))
        self.c_avg.set_value(str(m["average_size_formatted"]))
        self.c_rate.set_value(f"{m['success_rate']}%")
        self.c_ext.set_value(str(m["most_common_extension"]))

        for child in self.charts_frame.winfo_children():
            child.destroy()

        if not MATPLOTLIB_AVAILABLE:
            tk.Label(
                self.charts_frame,
                text=(
                    "Matplotlib is not installed in this environment.\n"
                    "Run 'pip install matplotlib Pillow' to enable interactive charts."
                ),
                bg=self.palette["card"],
                fg=self.palette["warning"],
                font=("Segoe UI", 11),
                padx=20,
                pady=30,
            ).pack(fill="both", expand=True)
            return

        for col in range(3):
            self.charts_frame.grid_columnconfigure(col, weight=1)
        self.charts_frame.grid_rowconfigure(0, weight=1)

        figs = [
            build_category_pie_figure(m, self.dark_mode),
            build_category_bar_figure(m, self.dark_mode),
            build_storage_bar_figure(m, self.dark_mode),
        ]
        for idx, fig in enumerate(figs):
            if fig is None:
                continue
            card = tk.Frame(
                self.charts_frame,
                bg=self.palette["card"],
                highlightbackground=self.palette["card_border"],
                highlightthickness=1,
            )
            card.grid(row=0, column=idx, sticky="nsew", padx=4)
            canvas = FigureCanvasTkAgg(fig, master=card)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
