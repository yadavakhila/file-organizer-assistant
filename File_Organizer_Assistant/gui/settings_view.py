"""Custom Rules & Settings view."""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict

from core.app_service import AppService
from gui.components import create_action_button


class SettingsView(tk.Frame):
    """Configure custom extensions, custom categories, folder names, and preferences."""

    def __init__(
        self,
        parent: tk.Misc,
        service: AppService,
        on_theme_change: Callable[[], None],
        palette: Dict[str, str],
    ) -> None:
        super().__init__(parent, bg=palette["bg"])
        self.service = service
        self.on_theme_change = on_theme_change
        self.palette = palette

        self.subfolders_var = tk.BooleanVar()
        self.hidden_var = tk.BooleanVar()
        self.sha256_var = tk.BooleanVar()
        self.conflict_var = tk.StringVar()
        self.theme_var = tk.StringVar()

        self.ext_cat_var = tk.StringVar()
        self.ext_val_var = tk.StringVar()
        self.new_cat_var = tk.StringVar()
        self.new_cat_exts_var = tk.StringVar()
        self.rename_cat_var = tk.StringVar()
        self.rename_folder_var = tk.StringVar()

        pref_card = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        pref_card.pack(fill="x", pady=(0, 12))

        tk.Label(
            pref_card,
            text="Organization Preferences",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        tk.Checkbutton(
            pref_card,
            text="Include Subfolders during Scan",
            variable=self.subfolders_var,
            bg=palette["card"],
            fg=palette["text"],
            selectcolor=palette["input_bg"],
            activebackground=palette["card"],
            activeforeground=palette["text"],
        ).pack(anchor="w", pady=2)

        tk.Checkbutton(
            pref_card,
            text="Include Hidden Files (starting with '.')",
            variable=self.hidden_var,
            bg=palette["card"],
            fg=palette["text"],
            selectcolor=palette["input_bg"],
            activebackground=palette["card"],
            activeforeground=palette["text"],
        ).pack(anchor="w", pady=2)

        tk.Checkbutton(
            pref_card,
            text="Verify Identical Duplicates with SHA-256",
            variable=self.sha256_var,
            bg=palette["card"],
            fg=palette["text"],
            selectcolor=palette["input_bg"],
            activebackground=palette["card"],
            activeforeground=palette["text"],
        ).pack(anchor="w", pady=2)

        pol_row = tk.Frame(pref_card, bg=palette["card"])
        pol_row.pack(anchor="w", pady=(8, 4))
        tk.Label(pol_row, text="Conflict Policy:", bg=palette["card"], fg=palette["muted"]).pack(
            side="left", padx=(0, 8)
        )
        tk.Radiobutton(
            pol_row,
            text="Skip (Safe Default)",
            variable=self.conflict_var,
            value="skip",
            bg=palette["card"],
            fg=palette["text"],
            selectcolor=palette["input_bg"],
        ).pack(side="left", padx=(0, 12))
        tk.Radiobutton(
            pol_row,
            text="Auto-Rename (name (1).ext)",
            variable=self.conflict_var,
            value="rename",
            bg=palette["card"],
            fg=palette["text"],
            selectcolor=palette["input_bg"],
        ).pack(side="left")

        theme_row = tk.Frame(pref_card, bg=palette["card"])
        theme_row.pack(anchor="w", pady=(4, 10))
        tk.Label(theme_row, text="UI Theme:", bg=palette["card"], fg=palette["muted"]).pack(
            side="left", padx=(0, 8)
        )
        tk.Radiobutton(
            theme_row,
            text="Dark Navy",
            variable=self.theme_var,
            value="dark",
            bg=palette["card"],
            fg=palette["text"],
            selectcolor=palette["input_bg"],
        ).pack(side="left", padx=(0, 12))
        tk.Radiobutton(
            theme_row,
            text="Light",
            variable=self.theme_var,
            value="light",
            bg=palette["card"],
            fg=palette["text"],
            selectcolor=palette["input_bg"],
        ).pack(side="left")

        btn_row = tk.Frame(pref_card, bg=palette["card"])
        btn_row.pack(anchor="w")
        create_action_button(btn_row, "Save Preferences", self._save_prefs, palette, "success").pack(
            side="left", padx=(0, 8)
        )
        create_action_button(btn_row, "Restore Defaults", self._restore_defaults, palette, "danger").pack(
            side="left"
        )

        # Custom Rules Card
        rules_card = tk.Frame(
            self,
            bg=palette["card"],
            highlightbackground=palette["card_border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        rules_card.pack(fill="both", expand=True)

        tk.Label(
            rules_card,
            text="Custom Categories & Extension Rules",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        # Row 1: Add extension
        r1 = tk.Frame(rules_card, bg=palette["card"])
        r1.pack(fill="x", pady=4)
        tk.Label(r1, text="Add Extension:", bg=palette["card"], fg=palette["muted"], width=16, anchor="w").pack(
            side="left"
        )
        self._entry(r1, self.ext_cat_var, "Category", 16).pack(side="left", padx=4)
        self._entry(r1, self.ext_val_var, ".ext", 12).pack(side="left", padx=4)
        create_action_button(r1, "Add Extension", self._add_extension, palette).pack(side="left", padx=6)

        # Row 2: Create category
        r2 = tk.Frame(rules_card, bg=palette["card"])
        r2.pack(fill="x", pady=4)
        tk.Label(r2, text="New Category:", bg=palette["card"], fg=palette["muted"], width=16, anchor="w").pack(
            side="left"
        )
        self._entry(r2, self.new_cat_var, "Category Name", 16).pack(side="left", padx=4)
        self._entry(r2, self.new_cat_exts_var, ".psd,.ai", 18).pack(side="left", padx=4)
        create_action_button(r2, "Create Category", self._create_category, palette).pack(side="left", padx=6)

        # Row 3: Rename folder
        r3 = tk.Frame(rules_card, bg=palette["card"])
        r3.pack(fill="x", pady=4)
        tk.Label(r3, text="Rename Folder:", bg=palette["card"], fg=palette["muted"], width=16, anchor="w").pack(
            side="left"
        )
        self._entry(r3, self.rename_cat_var, "Category", 16).pack(side="left", padx=4)
        self._entry(r3, self.rename_folder_var, "Folder Name", 18).pack(side="left", padx=4)
        create_action_button(r3, "Set Folder Name", self._rename_folder, palette).pack(side="left", padx=6)

    def _entry(self, parent: tk.Misc, var: tk.StringVar, _hint: str, width: int) -> tk.Entry:
        return tk.Entry(
            parent,
            textvariable=var,
            bg=self.palette["input_bg"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            relief="flat",
            width=width,
        )

    def refresh(self) -> None:
        s = self.service.rules_manager.settings
        self.subfolders_var.set(bool(s.get("include_subfolders", False)))
        self.hidden_var.set(bool(s.get("include_hidden_files", False)))
        self.sha256_var.set(bool(s.get("check_sha256_duplicates", True)))
        self.conflict_var.set(str(s.get("conflict_policy", "skip")))
        self.theme_var.set(str(s.get("theme", "dark")))

    def _save_prefs(self) -> None:
        old_theme = self.service.rules_manager.settings.get("theme", "dark")
        self.service.rules_manager.set_preference("include_subfolders", self.subfolders_var.get())
        self.service.rules_manager.set_preference("include_hidden_files", self.hidden_var.get())
        self.service.rules_manager.set_preference("check_sha256_duplicates", self.sha256_var.get())
        self.service.rules_manager.set_preference("conflict_policy", self.conflict_var.get())
        self.service.rules_manager.set_preference("theme", self.theme_var.get())
        self.service.save_settings()
        if old_theme != self.theme_var.get():
            self.on_theme_change()
        else:
            messagebox.showinfo("Settings Saved", "Preferences saved to settings.json.")

    def _restore_defaults(self) -> None:
        if messagebox.askyesno("Restore Defaults", "Reset all rules and preferences to defaults?"):
            self.service.restore_default_settings()
            self.refresh()
            self.on_theme_change()

    def _add_extension(self) -> None:
        ok, msg = self.service.rules_manager.add_custom_extension(
            self.ext_cat_var.get(), self.ext_val_var.get()
        )
        if ok:
            self.service.save_settings()
            messagebox.showinfo("Rule Added", msg)
        else:
            messagebox.showerror("Validation Error", msg)

    def _create_category(self) -> None:
        exts = [e.strip() for e in self.new_cat_exts_var.get().split(",") if e.strip()]
        ok, msg = self.service.rules_manager.create_custom_category(self.new_cat_var.get(), exts)
        if ok:
            self.service.save_settings()
            messagebox.showinfo("Category Created", msg)
        else:
            messagebox.showerror("Validation Error", msg)

    def _rename_folder(self) -> None:
        ok, msg = self.service.rules_manager.rename_category_folder(
            self.rename_cat_var.get(), self.rename_folder_var.get()
        )
        if ok:
            self.service.save_settings()
            messagebox.showinfo("Folder Renamed", msg)
        else:
            messagebox.showerror("Validation Error", msg)
