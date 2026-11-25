"""Dashboard & Welcome view displaying real metrics, quick actions, and recent activity."""

import tkinter as tk
from typing import Callable, Dict

from config.settings import APP_NAME, PROJECT_CODE
from core.app_service import AppService
from gui.components import StatCard, create_action_button, create_scrolled_treeview


class DashboardView(tk.Frame):
    """Main dashboard screen with live statistics and quick-action buttons."""

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

        # Welcome header
        header = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        header.pack(fill="x", pady=(0, 14))

        tk.Label(
            header,
            text=f"Welcome to {APP_NAME}",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 17, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text=f"{PROJECT_CODE}  |  Local-first, non-destructive preview & smart file organization",
            bg=palette["card"],
            fg=palette["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(3, 10))

        actions = tk.Frame(header, bg=palette["card"])
        actions.pack(anchor="w")
        create_action_button(
            actions, "Scan a Folder", lambda: self.navigate("scanner"), palette
        ).pack(side="left", padx=(0, 8))
        create_action_button(
            actions, "Preview & Organize", lambda: self.navigate("preview"), palette, "success"
        ).pack(side="left", padx=(0, 8))
        create_action_button(
            actions, "View Analytics", lambda: self.navigate("analytics"), palette
        ).pack(side="left", padx=(0, 8))
        create_action_button(
            actions, "Export Reports", lambda: self.navigate("reports"), palette
        ).pack(side="left")

        # KPI Cards grid
        cards_frame = tk.Frame(self, bg=palette["bg"])
        cards_frame.pack(fill="x", pady=(0, 14))
        for col in range(4):
            cards_frame.grid_columnconfigure(col, weight=1)

        self.card_scanned = StatCard(cards_frame, "Total Files Scanned", "0", palette, palette["accent"])
        self.card_organized = StatCard(cards_frame, "Files Organized", "0", palette, palette["success"])
        self.card_skipped = StatCard(cards_frame, "Skipped / Conflicts", "0", palette, palette["warning"])
        self.card_failed = StatCard(cards_frame, "Failed Operations", "0", palette, palette["danger"])

        self.card_scanned.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        self.card_organized.grid(row=0, column=1, sticky="nsew", padx=4, pady=(0, 8))
        self.card_skipped.grid(row=0, column=2, sticky="nsew", padx=4, pady=(0, 8))
        self.card_failed.grid(row=0, column=3, sticky="nsew", padx=(8, 0), pady=(0, 8))

        self.card_categories = StatCard(cards_frame, "Supported Categories", "0", palette)
        self.card_storage = StatCard(cards_frame, "Storage Processed", "0 B", palette)
        self.card_rate = StatCard(cards_frame, "Success Rate", "0.0%", palette, palette["success"])
        self.card_top_ext = StatCard(cards_frame, "Top Extension", "N/A", palette)

        self.card_categories.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self.card_storage.grid(row=1, column=1, sticky="nsew", padx=4)
        self.card_rate.grid(row=1, column=2, sticky="nsew", padx=4)
        self.card_top_ext.grid(row=1, column=3, sticky="nsew", padx=(8, 0))

        # Recent Activity section
        recent_box = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        recent_box.pack(fill="both", expand=True)

        tk.Label(
            recent_box,
            text="Recent Activity Log",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        table_container, self.activity_tree = create_scrolled_treeview(
            recent_box,
            [
                ("timestamp", "Timestamp", 150),
                ("action", "Action", 100),
                ("file_name", "File Name", 240),
                ("category", "Category", 130),
                ("status", "Status", 120),
            ],
        )
        table_container.pack(fill="both", expand=True)

    def refresh(self) -> None:
        """Reload live metrics and recent activity from persisted data."""
        m = self.service.get_metrics()
        self.card_scanned.set_value(str(m["total_files"]))
        self.card_organized.set_value(str(m["organized_files"]))
        self.card_skipped.set_value(str(m["skipped_files"]))
        self.card_failed.set_value(str(m["failed_files"]))
        self.card_categories.set_value(str(len(self.service.get_classifier().get_all_categories())))
        self.card_storage.set_value(str(m["total_storage_formatted"]))
        self.card_rate.set_value(f"{m['success_rate']}%")
        self.card_top_ext.set_value(str(m["most_common_extension"]))

        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        logs = self.service.csv_manager.load_activities(limit=25)
        for row in reversed(logs):
            self.activity_tree.insert(
                "",
                "end",
                values=(
                    row.get("timestamp", ""),
                    row.get("action", ""),
                    row.get("file_name", ""),
                    row.get("category", ""),
                    row.get("status", ""),
                ),
            )
