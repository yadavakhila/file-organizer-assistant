"""Main Tkinter application window coordinating sidebar navigation and all views."""

import tkinter as tk
from typing import Dict

from config.settings import APP_NAME, APP_VERSION
from core.app_service import AppService
from gui.analytics_view import AnalyticsView
from gui.components import configure_ttk_styles, get_palette
from gui.dashboard import DashboardView
from gui.explorer_view import ExplorerView
from gui.history_view import HistoryView
from gui.preview_view import PreviewView
from gui.reports_view import AboutView, ClassificationView, ReportsView
from gui.scanner_view import ScannerView
from gui.settings_view import SettingsView
from gui.sidebar import Sidebar


class FileOrganizerGUI:
    """Top-level Tkinter desktop application controller."""

    def __init__(self, service: AppService | None = None) -> None:
        self.service = service or AppService()
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1200x740")
        self.root.minsize(980, 620)

        self.views: Dict[str, tk.Frame] = {}
        self.current_view = "dashboard"
        self._build_ui()
        self._bind_shortcuts()
        self.navigate("dashboard")

    def _build_ui(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()

        theme_name = str(self.service.rules_manager.settings.get("theme", "dark"))
        self.palette = get_palette(theme_name)
        self.root.configure(bg=self.palette["bg"])
        configure_ttk_styles(self.root, self.palette)

        self.sidebar = Sidebar(self.root, self.navigate, self.palette)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(self.root, bg=self.palette["bg"], padx=16, pady=14)
        self.content.pack(side="left", fill="both", expand=True)

        self.views = {
            "dashboard": DashboardView(self.content, self.service, self.navigate, self.palette),
            "scanner": ScannerView(self.content, self.service, self.navigate, self.palette),
            "preview": PreviewView(self.content, self.service, self.navigate, self.palette),
            "classification": ClassificationView(self.content, self.service, self.palette),
            "explorer": ExplorerView(self.content, self.service, self.palette),
            "analytics": AnalyticsView(self.content, self.service, self.palette),
            "history": HistoryView(self.content, self.service, self.palette),
            "settings": SettingsView(self.content, self.service, self._rebuild_theme, self.palette),
            "reports": ReportsView(self.content, self.service, self.palette),
            "about": AboutView(self.content, self.palette),
        }

    def _rebuild_theme(self) -> None:
        current = self.current_view
        self._build_ui()
        self.navigate(current)

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-d>", lambda _e: self.navigate("dashboard"))
        self.root.bind("<Control-s>", lambda _e: self.navigate("scanner"))
        self.root.bind("<Control-p>", lambda _e: self.navigate("preview"))
        self.root.bind("<Control-f>", lambda _e: self.navigate("explorer"))

    def navigate(self, key: str) -> None:
        """Switch active view and refresh its live data."""
        if key not in self.views:
            return
        self.current_view = key
        for v in self.views.values():
            v.pack_forget()
        target = self.views[key]
        target.pack(fill="both", expand=True)
        if hasattr(target, "refresh"):
            target.refresh()
        self.sidebar.set_active(key)

    def run(self) -> None:
        """Start the Tkinter main event loop."""
        self.root.mainloop()


def launch_gui(service: AppService | None = None) -> None:
    """Entry helper to start the Tkinter GUI."""
    app = FileOrganizerGUI(service=service)
    app.run()
