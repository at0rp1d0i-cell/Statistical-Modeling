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


DEFAULT_DML_TABLE = TABLES_DIR / "table_02_dml_main_and_robustness.csv"
DEFAULT_DML_INPUT = INTERIM_DATA_DIR / "modeling" / "dml_candidate_input_2019_2023.csv"
DEFAULT_CATE = INTERIM_DATA_DIR / "modeling" / "heterogeneity_candidate_cate.csv"
DEFAULT_POLICY_PANEL = INTERIM_DATA_DIR / "policy_text" / "policy_mechanism_seed_panel_2019_2023.csv"
DEFAULT_MANIFEST = FIGURES_DIR / "figure_manifest.csv"

POLICY_COLUMNS = {
    "sum_policy_strength_city_year": "Policy strength",
    "mean_execution_clarity_city_year": "Execution clarity",
    "mean_digital_green_synergy_city_year": "Digital-green synergy",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export first-pass paper figures from current result artifacts.")
    parser.add_argument("--dml-table-path", type=Path, default=DEFAULT_DML_TABLE)
    parser.add_argument("--dml-input-path", type=Path, default=DEFAULT_DML_INPUT)
    parser.add_argument("--cate-path", type=Path, default=DEFAULT_CATE)
    parser.add_argument("--policy-panel-path", type=Path, default=DEFAULT_POLICY_PANEL)
    parser.add_argument("--output-dir", type=Path, default=FIGURES_DIR)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_MANIFEST)
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


def require_columns(frame: pd.DataFrame, required: list[str], source: Path) -> None:
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"{source} missing required columns: {missing}")


def format_source(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def save_figure(fig: plt.Figure, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return output_path


def normalize_first_year(series: pd.Series) -> pd.Series:
    first_valid = series.dropna().iloc[0]
    if first_valid == 0:
        return series
    return series / first_valid * 100


def export_trend_figure(frame: pd.DataFrame, output_dir: Path, source_path: Path = DEFAULT_DML_INPUT) -> dict[str, object]:
    source_columns = ["year", "digital_inclusive_finance_index", "co2_emission_intensity"]
    require_columns(frame, source_columns, source_path)
    trend = (
        frame[source_columns]
        .dropna()
        .groupby("year", as_index=True)
        .mean(numeric_only=True)
        .sort_index()
    )
    if trend.empty:
        raise ValueError(f"{source_path} has no non-missing rows for trend plotting")
    trend["digital_finance_index_2019_100"] = normalize_first_year(trend["digital_inclusive_finance_index"])
    trend["carbon_intensity_2019_100"] = normalize_first_year(trend["co2_emission_intensity"])

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(
        trend.index,
        trend["digital_finance_index_2019_100"],
        marker="o",
        linewidth=1.8,
        label="Digital inclusive finance (base=100)",
    )
    ax.plot(
        trend.index,
        trend["carbon_intensity_2019_100"],
        marker="s",
        linewidth=1.8,
        label="Carbon intensity (base=100)",
    )
    ax.set_title("Digital finance and carbon intensity trends")
    ax.set_xlabel("Year")
    ax.set_ylabel("Index, first observed year = 100")
    ax.legend(frameon=False)
    ax.set_xticks(trend.index.tolist())
    path = save_figure(fig, output_dir / "figure_01_digital_finance_carbon_intensity_trends.pdf")
    return {
        "figure_id": "Figure 1",
        "filename": path.name,
        "caption_cn": "数字普惠金融与碳排放强度年度趋势（首年=100）",
        "caption_en": "Annual trends in digital inclusive finance and carbon intensity (first year=100)",
        "source": format_source(source_path),
        "status": "first_pass",
        "caveat": "Descriptive trend only; not causal evidence.",
    }


def export_dml_interval_figure(frame: pd.DataFrame, output_dir: Path, source_path: Path = DEFAULT_DML_TABLE) -> dict[str, object]:
    required = ["ate", "ci_lower", "ci_upper"]
    require_columns(frame, required, source_path)
    if frame.empty:
        raise ValueError(f"{source_path} has no rows for DML interval plotting")
    labels = (
        frame["outcome_label_en"]
        if "outcome_label_en" in frame.columns
        else frame.get("outcome_column", pd.Series([f"Outcome {idx + 1}" for idx in range(len(frame))]))
    )

    fig, axes = plt.subplots(nrows=len(frame), ncols=1, figsize=(7.2, max(2.8, 2.2 * len(frame))))
    if len(frame) == 1:
        axes = [axes]
    for ax, (_, row), label in zip(axes, frame.iterrows(), labels):
        ate = float(row["ate"])
        ci_lower = float(row["ci_lower"])
        ci_upper = float(row["ci_upper"])
        ax.errorbar(
            ate,
            0,
            xerr=[[ate - ci_lower], [ci_upper - ate]],
            fmt="o",
            color="#2f5597",
            ecolor="#2f5597",
            capsize=4,
        )
        ax.axvline(0, color="#666666", linestyle="--", linewidth=1)
        ax.set_yticks([])
        ax.set_title(str(label))
        ax.set_xlabel("Estimated effect and 95% CI")
    path = save_figure(fig, output_dir / "figure_02_dml_effect_intervals.pdf")
    return {
        "figure_id": "Figure 2",
        "filename": path.name,
        "caption_cn": "DML 主结果与稳健性结果的估计区间",
        "caption_en": "DML effect intervals for main and robustness outcomes",
        "source": format_source(source_path),
        "status": "first_pass",
        "caveat": "Uses current scenario B specification without population candidate control.",
    }


def export_cate_distribution_figure(frame: pd.DataFrame, output_dir: Path, source_path: Path = DEFAULT_CATE) -> dict[str, object]:
    require_columns(frame, ["cate_hat"], source_path)
    cate = frame["cate_hat"].dropna()
    if cate.empty:
        raise ValueError(f"{source_path} has no non-missing CATE values")
    bins = max(4, min(30, int(len(cate) ** 0.5)))
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.hist(cate, bins=bins, color="#7f7f7f", edgecolor="white")
    ax.axvline(cate.mean(), color="#2f5597", linestyle="--", linewidth=1.5, label=f"Mean = {cate.mean():.4f}")
    ax.axvline(0, color="#444444", linestyle=":", linewidth=1)
    ax.set_title("Candidate CATE distribution")
    ax.set_xlabel("Estimated CATE")
    ax.set_ylabel("Frequency")
    ax.legend(frameon=False)
    path = save_figure(fig, output_dir / "figure_03_candidate_cate_distribution.pdf")
    return {
        "figure_id": "Figure 3",
        "filename": path.name,
        "caption_cn": "候选 CATE 分布（非最终 headline 异质性结论）",
        "caption_en": "Candidate CATE distribution (non-final heterogeneity result)",
        "source": format_source(source_path),
        "status": "candidate_non_final",
        "caveat": "Headline heterogeneity features remain a research-design decision.",
    }


def export_policy_seed_trend_figure(
    frame: pd.DataFrame,
    output_dir: Path,
    source_path: Path = DEFAULT_POLICY_PANEL,
) -> dict[str, object]:
    required = ["year", *POLICY_COLUMNS.keys()]
    require_columns(frame, required, source_path)
    trend = frame[required].groupby("year", as_index=True).mean(numeric_only=True).sort_index()

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    if trend.dropna(how="all").empty:
        ax.text(0.5, 0.5, "No non-missing seed policy scores", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    else:
        for column, label in POLICY_COLUMNS.items():
            ax.plot(trend.index, trend[column], marker="o", linewidth=1.6, label=label)
        ax.set_title("Seed policy mechanism trends")
        ax.set_xlabel("Year")
        ax.set_ylabel("Annual mean score")
        ax.set_xticks(trend.index.tolist())
        ax.legend(frameon=False)
    path = save_figure(fig, output_dir / "figure_04_policy_seed_mechanism_trends.pdf")
    return {
        "figure_id": "Figure 4",
        "filename": path.name,
        "caption_cn": "政策文本 seed 机制变量年度趋势（规则代理）",
        "caption_en": "Annual trends in seed policy-text mechanism variables (rule proxy)",
        "source": format_source(source_path),
        "status": "seed_rule_proxy_non_final",
        "caveat": "Seed central-document rule proxy only; not validated LLM scoring.",
    }


def export_manifest(records: list[dict[str, object]], manifest_path: Path) -> Path:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(manifest_path, index=False)
    return manifest_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_project_directories()
    configure_style()

    dml_table = pd.read_csv(args.dml_table_path)
    dml_input = pd.read_csv(args.dml_input_path)
    cate = pd.read_csv(args.cate_path)
    policy_panel = pd.read_csv(args.policy_panel_path)

    records = [
        export_trend_figure(dml_input, args.output_dir, args.dml_input_path),
        export_dml_interval_figure(dml_table, args.output_dir, args.dml_table_path),
        export_cate_distribution_figure(cate, args.output_dir, args.cate_path),
        export_policy_seed_trend_figure(policy_panel, args.output_dir, args.policy_panel_path),
    ]
    manifest_path = export_manifest(records, args.manifest_path)
    print(f"Figures written to: {args.output_dir}")
    print(f"Figure manifest written to: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
