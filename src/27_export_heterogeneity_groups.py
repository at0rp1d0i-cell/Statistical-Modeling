import argparse
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd

from stat_modeling.config import FIGURES_DIR
from stat_modeling.config import INTERIM_DATA_DIR
from stat_modeling.config import TABLES_DIR
from stat_modeling.config import ensure_project_directories
from stat_modeling.delivery.figure_formats import save_figure_with_rasters
from stat_modeling.data.io import write_table
from stat_modeling.modeling.heterogeneity_groups import build_heterogeneity_group_summary


DEFAULT_CATE_PATH = INTERIM_DATA_DIR / "modeling" / "heterogeneity_candidate_cate.csv"
DEFAULT_MODEL_INPUT_PATH = INTERIM_DATA_DIR / "modeling" / "dml_candidate_input_2019_2023.csv"
DEFAULT_OUTPUT_CSV = TABLES_DIR / "table_10_heterogeneity_group_summary.csv"
DEFAULT_OUTPUT_TEX = TABLES_DIR / "table_10_heterogeneity_group_summary.tex"
DEFAULT_ATTACHED_CSV = INTERIM_DATA_DIR / "modeling" / "heterogeneity_candidate_cate_with_groups.csv"
DEFAULT_FIGURE_PATH = FIGURES_DIR / "figure_06_heterogeneity_groups.pdf"

DIMENSION_EN = {
    "区域": "Region",
    "经济发展水平": "Economic development",
    "产业结构": "Industrial structure",
}
GROUP_EN = {
    "东部": "East",
    "中部": "Central",
    "西部": "West",
    "东北": "Northeast",
    "高经济发展水平": "High GDP",
    "低经济发展水平": "Low GDP",
    "高第二产业占比": "High secondary share",
    "低第二产业占比": "Low secondary share",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export formal heterogeneity group summaries from candidate CATE output.")
    parser.add_argument("--cate-path", type=Path, default=DEFAULT_CATE_PATH)
    parser.add_argument("--model-input-path", type=Path, default=DEFAULT_MODEL_INPUT_PATH)
    parser.add_argument("--output-csv-path", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-tex-path", type=Path, default=DEFAULT_OUTPUT_TEX)
    parser.add_argument("--attached-csv-path", type=Path, default=DEFAULT_ATTACHED_CSV)
    parser.add_argument("--figure-path", type=Path, default=DEFAULT_FIGURE_PATH)
    return parser


def configure_style() -> None:
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    serif_font = "Times New Roman" if "Times New Roman" in available_fonts else "DejaVu Sans"
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "font.family": [serif_font],
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def format_latex_table(summary: pd.DataFrame) -> str:
    display = summary[
        [
            "dimension_cn",
            "group_cn",
            "n_city",
            "n_obs",
            "cate_mean",
            "cate_mean_ci_lower_approx",
            "cate_mean_ci_upper_approx",
            "cate_median",
            "grouping_rule",
        ]
    ].copy()
    display.columns = [
        "异质性维度",
        "分组",
        "城市数",
        "观测数",
        "CATE均值",
        "均值CI下限(近似)",
        "均值CI上限(近似)",
        "CATE中位数",
        "分组规则",
    ]
    for column in ["CATE均值", "均值CI下限(近似)", "均值CI上限(近似)", "CATE中位数"]:
        display[column] = display[column].map(lambda value: f"{float(value):.4f}")
    for column in ["城市数", "观测数"]:
        display[column] = display[column].astype(int).astype(str)
    return display.to_latex(
        index=False,
        escape=False,
        caption="正式异质性分组摘要（基于当前 CATE 候选估计）",
        label="tab:heterogeneity_group_summary",
    )


def export_group_figure(summary: pd.DataFrame, figure_path: Path) -> Path:
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    plot = summary.copy()
    plot["label_en"] = plot.apply(
        lambda row: f"{DIMENSION_EN.get(row['dimension_cn'], row['dimension_cn'])}: {GROUP_EN.get(row['group_cn'], row['group_cn'])}",
        axis=1,
    )
    y_positions = list(range(len(plot)))
    x = plot["cate_mean"].astype(float)
    xerr_lower = x - plot["cate_mean_ci_lower_approx"].astype(float)
    xerr_upper = plot["cate_mean_ci_upper_approx"].astype(float) - x

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.errorbar(
        x,
        y_positions,
        xerr=[xerr_lower, xerr_upper],
        fmt="o",
        color="#2f5597",
        ecolor="#7f7f7f",
        capsize=3,
    )
    ax.axvline(0, color="#444444", linestyle="--", linewidth=1)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(plot["label_en"].tolist())
    ax.invert_yaxis()
    ax.set_xlabel("Group mean CATE and approximate 95% interval")
    ax.set_title("Heterogeneity group summaries")
    ax.text(
        0.0,
        -0.12,
        "Note: intervals summarize current candidate CATE estimates; not a subgroup significance test.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        color="#444444",
    )
    fig.tight_layout()
    save_figure_with_rasters(fig, figure_path)
    plt.close(fig)
    return figure_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_project_directories()
    configure_style()

    cate = pd.read_csv(args.cate_path)
    model_input = pd.read_csv(args.model_input_path)
    summary, attached = build_heterogeneity_group_summary(cate, model_input)

    csv_path = write_table(summary, args.output_csv_path)
    args.output_tex_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_tex_path.write_text(format_latex_table(summary), encoding="utf-8")
    attached_path = write_table(attached, args.attached_csv_path)
    figure_path = export_group_figure(summary, args.figure_path)

    print(f"Heterogeneity group summary CSV written to: {csv_path}")
    print(f"Heterogeneity group summary LaTeX written to: {args.output_tex_path}")
    print(f"CATE rows with groups written to: {attached_path}")
    print(f"Heterogeneity group figure written to: {figure_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
