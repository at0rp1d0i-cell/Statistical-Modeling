"""Figure export helpers for paper-facing PDF and raster assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable


DEFAULT_RASTER_FORMATS = ("png", "jpg")


def companion_figure_paths(pdf_path: Path, raster_formats: Iterable[str] = DEFAULT_RASTER_FORMATS) -> dict[str, Path]:
    """Return the canonical PDF/raster output paths for a paper figure."""
    paths = {"pdf": pdf_path}
    for raster_format in raster_formats:
        normalized = "jpg" if raster_format.lower() in {"jpg", "jpeg"} else raster_format.lower()
        paths[normalized] = pdf_path.with_suffix(f".{normalized}")
    return paths


def save_figure_with_rasters(
    fig: Any,
    pdf_path: Path,
    raster_formats: Iterable[str] = DEFAULT_RASTER_FORMATS,
    dpi: int = 300,
) -> dict[str, Path]:
    """Save a matplotlib figure as PDF plus PNG/JPG companion files."""
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    outputs = companion_figure_paths(pdf_path, raster_formats)
    for output_format, path in outputs.items():
        if output_format == "pdf":
            continue
        save_format = "jpeg" if output_format == "jpg" else output_format
        fig.savefig(path, format=save_format, dpi=dpi, bbox_inches="tight", facecolor="white")
    return outputs
