# File Organizer Assistant

**Official Assigned Project:** SmartCommunity Hack – Project #105  
**Subject:** Python Programming  
**Domain:** Digital Tools & Productivity  

---

## 1. Problem Statement
Users frequently accumulate hundreds of unorganized files (documents, images, archives, scripts, spreadsheets, installers) in a single folder. Manually sorting files is tedious and error-prone, while naive scripts risk overwriting existing files or moving files without user visibility.

## 2. Project Objectives
- Build a local-first Python application that scans a user-selected directory and classifies files by extension.
- Provide a **mandatory interactive terminal interface** and an **optional Tkinter desktop GUI** backed by the same core engine.
- Guarantee a **100% non-destructive Preview Mode** before any file is moved, renamed, or deleted.
- Prevent data loss through **SHA-256 duplicate detection**, zero-overwrite conflict handling, protected system-directory blocking, and **Safe Undo**.
- Persist scan/organization records in JSON and CSV formats and generate executive analytics and exportable reports (CSV, JSON, Markdown, TXT).

## 3. Technology Stack
| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.10+ | Core application |
| Terminal UI | Standard Input/Output (`cli.py`) | Mandatory menu-driven interface |
| Desktop GUI | Tkinter + `ttk` (`gui/`) | Optional dark/light productivity UI |
| Filesystem | `pathlib`, `shutil`, `os` | Safe scanning & file movement |
| Persistence | `json`, `csv` | Records, settings, history, activity log |
| Integrity | `hashlib` (SHA-256) | Duplicate content verification |
| Analytics | `collections.Counter`, `statistics`, `matplotlib` | Metrics & visual charts |
| Validation | `re`, `pathlib` | Defensive input & path validation |
| Logging & QA | `logging`, `unittest` | Audit logs & automated tests |

## 4. Python Concepts Demonstrated
- **Object-Oriented Programming:** Modular classes (`AppService`, `FileScanner`, `FileClassifier`, `PreviewEngine`, `FileOrganizer`, `JSONManager`, `CSVManager`, `StatisticsEngine`, `FileOrganizerGUI`).
- **Data Structures:** Dictionaries for O(1) extension-to-category lookup, sets for planned destination tracking, dataclasses for structured records, lists and comprehensions for filtering/sorting.
- **Exception Handling & Defensive Validation:** Handling `PermissionError`, `FileNotFoundError`, `OSError`, `json.JSONDecodeError`, and regex validation.
- **Concurrency:** Background `threading.Thread` with `after()` GUI-thread marshaling in Tkinter so large scans do not freeze the interface.

## 5. Project Folder Structure
```text
File_Organizer_Assistant/
├── main.py                        # Entry point (--cli or --gui)
├── cli.py                         # Interactive terminal menu interface
├── requirements.txt               # matplotlib, Pillow
├── README.md
├── .gitignore
├── config/
│   ├── __init__.py
│   ├── settings.py                # Paths, constants, protected OS dirs
│   └── categories.py              # Default extension-to-category mappings
├── core/
│   ├── __init__.py
│   ├── app_service.py             # Unified facade shared by CLI and GUI
│   ├── scanner.py                 # Safe directory scanner
│   ├── classifier.py              # Case-insensitive extension classifier
│   ├── preview.py                 # Non-destructive preview engine
│   ├── organizer.py               # Safe file mover & undo engine
│   ├── duplicate_checker.py       # Filename & SHA-256 duplicate detection
│   ├── conflict_handler.py        # Skip / safe-rename conflict resolution
│   ├── custom_rules.py            # Custom categories, extensions, preferences
│   └── search_engine.py           # Multi-criteria search & sorting
├── database/
│   ├── __init__.py
│   ├── json_manager.py            # file_records.json & settings.json
│   ├── csv_manager.py             # activity_log.csv & bulk CSV import
│   └── history_manager.py         # organization_history.json
├── analytics/
│   ├── __init__.py
│   ├── statistics_engine.py       # Executive metrics & zero-safe formulas
│   └── charts.py                  # Matplotlib pie, bar, and storage charts
├── reports/
│   ├── __init__.py
│   └── export_manager.py          # CSV, JSON, Markdown, TXT report exports
├── utils/
│   ├── __init__.py
│   ├── validators.py              # Path, category, extension, confirmation checks
│   ├── logger.py                  # Application logging to logs/application.log
│   ├── file_utils.py              # Size formatting & SHA-256 hashing
│   └── date_utils.py              # ISO timestamps & export slugs
├── gui/
│   ├── __init__.py
│   ├── app.py                     # Main Tkinter window & shortcuts
│   ├── components.py              # Dark/Light theme palettes & reusable widgets
│   ├── sidebar.py                 # Navigation rail
│   ├── dashboard.py               # Welcome, KPI cards, recent activity
│   ├── scanner_view.py            # Folder browser & threaded scanner
│   ├── preview_view.py            # Preview table & confirmation dialog
│   ├── explorer_view.py           # Search, filter, sort, bulk CSV import
│   ├── analytics_view.py          # Metrics & embedded Matplotlib charts
│   ├── history_view.py            # History table & Safe Undo
│   ├── settings_view.py           # Preferences, theme toggle, custom rules
│   └── reports_view.py            # Report exports, classification, about
├── tests/
│   ├── __init__.py
│   ├── test_validators.py
│   ├── test_scanner.py
│   ├── test_classifier.py
│   ├── test_preview.py
│   ├── test_organizer.py
│   ├── test_database.py
│   └── test_analytics_reports.py
├── data/
│   ├── file_records.json          # Pre-populated 35-record sample dataset
│   ├── settings.json
│   ├── organization_history.json
│   └── activity_log.csv
├── exports/
└── logs/
```

## 6. Installation & Setup
```powershell
cd File_Organizer_Assistant
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
*(Note: The Terminal CLI and core Tkinter GUI also run with Python's standard library alone; `matplotlib` enables visual charts in the Analytics view.)*

## 7. Execution Commands
- **Run Interactive Terminal Interface (Default / Mandatory):**
  ```powershell
  python main.py --cli
  ```
- **Run Tkinter Desktop GUI:**
  ```powershell
  python main.py --gui
  ```
- **Run Automated Unit Tests:**
  ```powershell
  python -m unittest discover -s tests -v
  ```

## 8. Demonstration Guide
1. Launch `python main.py --cli` (or `--gui`).
2. Inspect the **Dashboard** (pre-loaded with 35 sample records across all categories, including Skipped and Failed boundary cases).
3. Use **Generate Safe Demo Test Folder** (CLI Option 9 or GUI Scanner "Demo Folder" button) to create a safe `sample_test_folder/` without touching personal files.
4. **Scan** `sample_test_folder` and inspect the **Preview** (no files are moved yet).
5. **Confirm Organization** to move files into categorized subfolders, then check **Analytics**, **File Explorer**, and **Export Reports**.
6. Restart the application to verify **JSON/CSV persistence**, or test **Undo Last Organization** in History.

## 9. Limitations & Future Enhancements
- **Current Limitations:** Duplicate content comparison checks destination collisions and batch duplicates rather than scanning across external drives; Tkinter charts require `matplotlib`.
- **Future Enhancements:** Scheduled background folder watching, drag-and-drop folder selection via `tkinterdnd2`, and rule-based filename pattern matching (regex/date-based subfoldering).
