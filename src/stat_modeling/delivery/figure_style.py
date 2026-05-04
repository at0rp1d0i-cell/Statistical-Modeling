"""Shared matplotlib style for paper-facing figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager


_CJK_FONT_PATHS = (
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"),
    Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
    Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
    Path("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"),
)


def _register_available_cjk_fonts() -> list[str]:
    """Register locally installed CJK fonts and return preferred font families."""

    for font_path in _CJK_FONT_PATHS:
        if font_path.exists():
            try:
                font_manager.fontManager.addfont(str(font_path))
            except RuntimeError:
                # Some TTC collections may already be registered or partially
                # unsupported by the active backend; continue to the next font.
                continue
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    preferred_fonts = [
        "Noto Sans CJK SC",
        "Noto Serif CJK SC",
        "WenQuanYi Zen Hei",
        "WenQuanYi Micro Hei",
        "Droid Sans Fallback",
        "SimSun",
        "Microsoft YaHei",
        "DejaVu Sans",
    ]
    return [font for font in preferred_fonts if font in available_fonts]


def configure_paper_figure_style() -> None:
    """Apply consistent Chinese-capable styling for paper figures."""

    cjk_fonts = _register_available_cjk_fonts()
    font_family = cjk_fonts or ["DejaVu Sans"]
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "font.family": font_family,
            "axes.unicode_minus": False,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
