"""Matplotlib chart builders for GUI embedding and image export."""

from typing import Any, Dict

try:
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    Figure = Any  # type: ignore
    MATPLOTLIB_AVAILABLE = False

CHART_PALETTE = [
    "#3B82F6",
    "#10B981",
    "#F59E0B",
    "#8B5CF6",
    "#EC4899",
    "#06B6D4",
    "#EF4444",
    "#6366F1",
    "#84CC16",
]


def _style_axes(ax: Any, dark_mode: bool = True) -> None:
    bg = "#131C2E" if dark_mode else "#FFFFFF"
    fg = "#E2E8F0" if dark_mode else "#1E293B"
    grid = "#24324D" if dark_mode else "#E2E8F0"
    ax.set_facecolor(bg)
    ax.tick_params(colors=fg, labelsize=8)
    ax.xaxis.label.set_color(fg)
    ax.yaxis.label.set_color(fg)
    ax.title.set_color(fg)
    for spine in ax.spines.values():
        spine.set_color(grid)


def build_category_pie_figure(metrics: Dict[str, Any], dark_mode: bool = True) -> Any:
    """Create a Matplotlib Figure showing category distribution donut chart."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    fig_bg = "#131C2E" if dark_mode else "#FFFFFF"
    fg = "#E2E8F0" if dark_mode else "#1E293B"
    fig = Figure(figsize=(4.8, 3.6), dpi=100, facecolor=fig_bg)
    ax = fig.add_subplot(111)
    _style_axes(ax, dark_mode)

    counts = metrics.get("category_counts", {})
    if not counts:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", color=fg, fontsize=11)
        ax.axis("off")
        return fig

    labels = list(counts.keys())
    values = list(counts.values())
    colors = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(labels))]

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        pctdistance=0.78,
        wedgeprops={"width": 0.45, "edgecolor": fig_bg},
        textprops={"color": fg, "fontsize": 8},
    )
    for autotext in autotexts:
        autotext.set_color("#FFFFFF")
        autotext.set_fontsize(7.5)
    ax.set_title("Files by Category", fontsize=10.5, fontweight="bold", pad=10)
    fig.tight_layout()
    return fig


def build_category_bar_figure(metrics: Dict[str, Any], dark_mode: bool = True) -> Any:
    """Create a Matplotlib Figure showing file counts per category."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    fig_bg = "#131C2E" if dark_mode else "#FFFFFF"
    fg = "#E2E8F0" if dark_mode else "#1E293B"
    fig = Figure(figsize=(4.8, 3.6), dpi=100, facecolor=fig_bg)
    ax = fig.add_subplot(111)
    _style_axes(ax, dark_mode)

    counts = metrics.get("category_counts", {})
    if not counts:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", color=fg, fontsize=11)
        ax.axis("off")
        return fig

    labels = list(counts.keys())
    values = list(counts.values())
    colors = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(labels))]

    bars = ax.bar(labels, values, color=colors, width=0.55)
    ax.set_title("File Count per Category", fontsize=10.5, fontweight="bold", pad=10)
    ax.set_ylabel("Files", fontsize=9)
    ax.tick_params(axis="x", rotation=30)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{int(height)}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            color=fg,
            fontsize=8,
        )
    fig.tight_layout()
    return fig


def build_storage_bar_figure(metrics: Dict[str, Any], dark_mode: bool = True) -> Any:
    """Create a Matplotlib Figure showing storage usage (KB) per category."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    fig_bg = "#131C2E" if dark_mode else "#FFFFFF"
    fg = "#E2E8F0" if dark_mode else "#1E293B"
    fig = Figure(figsize=(4.8, 3.6), dpi=100, facecolor=fig_bg)
    ax = fig.add_subplot(111)
    _style_axes(ax, dark_mode)

    storage = metrics.get("storage_by_category", {})
    if not storage:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", color=fg, fontsize=11)
        ax.axis("off")
        return fig

    labels = list(storage.keys())
    values_kb = [round(v / 1024.0, 2) for v in storage.values()]
    colors = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(labels))]

    ax.barh(labels, values_kb, color=colors)
    ax.invert_yaxis()
    ax.set_title("Storage Distribution (KB)", fontsize=10.5, fontweight="bold", pad=10)
    ax.set_xlabel("Size (KB)", fontsize=9)
    fig.tight_layout()
    return fig
