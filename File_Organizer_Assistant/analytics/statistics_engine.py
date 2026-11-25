"""Statistics engine for computing file organization metrics and summaries."""

import statistics
from collections import Counter, defaultdict
from typing import Any, Dict, List

from utils.file_utils import format_size


class StatisticsEngine:
    """Computes executive summary analytics from persisted file records."""

    def compute_metrics(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute all required analytics safely, handling empty datasets."""
        total_files = len(records)
        if total_files == 0:
            return {
                "total_files": 0,
                "organized_files": 0,
                "skipped_files": 0,
                "failed_files": 0,
                "scanned_only_files": 0,
                "success_rate": 0.0,
                "total_storage_bytes": 0,
                "total_storage_formatted": "0 B",
                "average_size_bytes": 0.0,
                "average_size_formatted": "0 B",
                "most_common_extension": "N/A",
                "category_counts": {},
                "storage_by_category": {},
                "extension_counts": {},
                "status_counts": {},
            }

        status_counter: Counter[str] = Counter()
        category_counter: Counter[str] = Counter()
        extension_counter: Counter[str] = Counter()
        storage_by_category: Dict[str, int] = defaultdict(int)
        sizes: List[int] = []

        for rec in records:
            status = str(rec.get("status", "Scanned"))
            category = str(rec.get("category", "Others"))
            ext = str(rec.get("extension", "") or "(none)").lower()
            size = int(rec.get("file_size", 0) or 0)

            status_counter[status] += 1
            category_counter[category] += 1
            extension_counter[ext] += 1
            storage_by_category[category] += size
            sizes.append(size)

        organized = status_counter.get("Organized", 0)
        skipped = status_counter.get("Skipped", 0)
        failed = status_counter.get("Failed", 0)
        scanned_only = status_counter.get("Scanned", 0)

        attempted = organized + skipped + failed
        success_rate = round((organized / attempted) * 100.0, 2) if attempted > 0 else 0.0

        total_storage = sum(sizes)
        avg_size = statistics.mean(sizes) if sizes else 0.0
        most_common_ext = extension_counter.most_common(1)[0][0] if extension_counter else "N/A"

        return {
            "total_files": total_files,
            "organized_files": organized,
            "skipped_files": skipped,
            "failed_files": failed,
            "scanned_only_files": scanned_only,
            "success_rate": success_rate,
            "total_storage_bytes": total_storage,
            "total_storage_formatted": format_size(total_storage),
            "average_size_bytes": round(avg_size, 2),
            "average_size_formatted": format_size(int(avg_size)),
            "most_common_extension": most_common_ext,
            "category_counts": dict(category_counter.most_common()),
            "storage_by_category": dict(
                sorted(storage_by_category.items(), key=lambda kv: kv[1], reverse=True)
            ),
            "extension_counts": dict(extension_counter.most_common(10)),
            "status_counts": dict(status_counter),
        }
