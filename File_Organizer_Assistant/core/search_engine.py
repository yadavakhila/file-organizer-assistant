"""Search, filtering, and sorting engine for persisted file records."""

from typing import Dict, List, Optional


class FileSearchEngine:
    """Filters and sorts file records by name, extension, category, size, status, and date."""

    def search_and_filter(
        self,
        records: List[Dict],
        query: str = "",
        extension: str = "",
        category: str = "All",
        status: str = "All",
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        sort_by: str = "file_name",
        descending: bool = False,
    ) -> List[Dict]:
        """Filter and sort a list of file record dictionaries."""
        q = query.strip().lower()
        ext_filter = extension.strip().lower()
        if ext_filter and not ext_filter.startswith("."):
            ext_filter = f".{ext_filter}"

        filtered: List[Dict] = []
        for rec in records:
            fname = str(rec.get("file_name", "")).lower()
            rec_ext = str(rec.get("extension", "")).lower()
            rec_cat = str(rec.get("category", ""))
            rec_status = str(rec.get("status", ""))
            rec_size = int(rec.get("file_size", 0) or 0)

            if q and q not in fname:
                continue
            if ext_filter and rec_ext != ext_filter:
                continue
            if category and category != "All" and rec_cat.lower() != category.lower():
                continue
            if status and status != "All" and rec_status.lower() != status.lower():
                continue
            if min_size is not None and rec_size < min_size:
                continue
            if max_size is not None and rec_size > max_size:
                continue

            filtered.append(rec)

        key_map = {
            "file_name": lambda r: str(r.get("file_name", "")).lower(),
            "file_size": lambda r: int(r.get("file_size", 0) or 0),
            "date": lambda r: str(r.get("date_scanned", "")),
            "category": lambda r: str(r.get("category", "")).lower(),
            "status": lambda r: str(r.get("status", "")).lower(),
        }
        sort_key = key_map.get(sort_by, key_map["file_name"])
        return sorted(filtered, key=sort_key, reverse=descending)
