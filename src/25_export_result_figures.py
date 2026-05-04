import argparse
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from stat_modeling.config import FIGURES_DIR
from stat_modeling.config import INTERIM_DATA_DIR
from stat_modeling.config import TABLES_DIR
from stat_modeling.config import ensure_project_directories
from stat_modeling.delivery.figure_formats import companion_figure_paths
from stat_modeling.delivery.figure_formats import save_figure_with_rasters
from stat_modeling.delivery.figure_style import configure_paper_figure_style


DEFAULT_DML_TABLE = TABLES_DIR / "table_02_dml_main_and_robustness.csv"
DEFAULT_DML_INPUT = INTERIM_DATA_DIR / "modeling" / "dml_candidate_input_2019_2023.csv"
DEFAULT_CATE = INTERIM_DATA_DIR / "modeling" / "heterogeneity_candidate_cate.csv"
DEFAULT_POLICY_PANEL = INTERIM_DATA_DIR / "policy_text" / "policy_mechanism_seed_panel_2019_2023.csv"
DEFAULT_MANIFEST = FIGURES_DIR / "figure_manifest.csv"

POLICY_SCORE_DISPLAY_COLUMNS = {
    "policy_strength_score": {
        "label": "政策强度",
        "preferred": "mean_policy_strength_city_year",
        "fallback": "sum_policy_strength_city_year",
    },
    "execution_clarity_score": {
        "label": "执行明确性",
        "preferred": "mean_execution_clarity_city_year",
        "fallback": "mean_execution_clarity_city_year",
    },
    "digital_green_synergy_score": {
        "label": "数字绿色协同度",
        "preferred": "mean_digital_green_synergy_city_year",
        "fallback": "mean_digital_green_synergy_city_year",
    },
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
    configure_paper_figure_style()


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
    outputs = save_figure_with_rasters(fig, output_path)
    plt.close(fig)
    return outputs["pdf"]


def add_companion_raster_fields(record: dict[str, object]) -> dict[str, object]:
    filename = record.get("filename")
    if isinstance(filename, str) and filename.endswith(".pdf"):
        paths = companion_figure_paths(Path(filename))
        record["png_filename"] = paths["png"].name
        record["jpg_filename"] = paths["jpg"].name
    return record


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
        label="数字普惠金融指数（首年=100）",
    )
    ax.plot(
        trend.index,
        trend["carbon_intensity_2019_100"],
        marker="s",
        linewidth=1.8,
        label="碳排放强度（首年=100）",
    )
    ax.set_title("数字普惠金融与碳排放强度年度趋势")
    ax.set_xlabel("年份")
    ax.set_ylabel("指数（首年=100）")
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
    required = ["ate", "ci_lower", "ci_upper", "p_value"]
    require_columns(frame, required, source_path)
    if frame.empty:
        raise ValueError(f"{source_path} has no rows for DML interval plotting")
    labels = frame["outcome_label_cn"] if "outcome_label_cn" in frame.columns else frame.get("outcome_column", pd.Series([f"结果 {idx + 1}" for idx in range(len(frame))]))

    fig, axes = plt.subplots(nrows=len(frame), ncols=1, figsize=(7.2, max(3.6, 2.5 * len(frame))))
    if len(frame) == 1:
        axes = [axes]
    fig.suptitle("DML 估计效应及 95% 置信区间", fontsize=13, y=0.99)
    for ax, (_, row), label in zip(axes, frame.iterrows(), labels):
        ate = float(row["ate"])
        ci_lower = float(row["ci_lower"])
        ci_upper = float(row["ci_upper"])
        p_value = float(row["p_value"])
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
        ax.set_xlabel("估计效应（结果变量原单位）")
        span = ci_upper - ci_lower
        padding = span * 0.08 if span else max(abs(ate) * 0.1, 0.01)
        ax.set_xlim(ci_lower - padding, max(0, ci_upper) + padding)
        annotation = f"ATE = {ate:.4f}\n95% 置信区间 [{ci_lower:.4f}, {ci_upper:.4f}]\np = {p_value:.4f}"
        ax.text(
            0.99,
            0.80,
            annotation,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=8.5,
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#dddddd", "alpha": 0.9},
        )
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
    ax.axvline(cate.mean(), color="#2f5597", linestyle="--", linewidth=1.5, label=f"均值 = {cate.mean():.4f}")
    ax.axvline(0, color="#444444", linestyle=":", linewidth=1)
    ax.set_title("候选 CATE 分布")
    ax.set_xlabel("估计 CATE")
    ax.set_ylabel("频数")
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


def export_policy_seed_snapshot_figure(
    frame: pd.DataFrame,
    output_dir: Path,
    source_path: Path = DEFAULT_POLICY_PANEL,
) -> dict[str, object]:
    require_columns(frame, ["year"], source_path)
    working = frame.copy()
    display_score_columns: dict[str, str] = {}
    for output_column, config in POLICY_SCORE_DISPLAY_COLUMNS.items():
        source_column = config["preferred"] if config["preferred"] in working.columns else config["fallback"]
        require_columns(working, [source_column], source_path)
        working[output_column] = working[source_column]
        display_score_columns[output_column] = config["label"]
    if "policy_doc_count" not in working.columns:
        working["policy_doc_count"] = working[list(display_score_columns)].notna().any(axis=1).astype(int)
    trend = (
        working[["year", "policy_doc_count", *display_score_columns.keys()]]
        .groupby("year", as_index=True)
        .agg(
            policy_doc_count=("policy_doc_count", "mean"),
            **{column: (column, "mean") for column in display_score_columns}
        )
        .sort_index()
    )
    active_scores = trend[list(display_score_columns)].dropna(how="all")

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8.2, 3.8), gridspec_kw={"width_ratios": [1.1, 1.4]})
    fig.suptitle("政策文本 seed 机制变量覆盖快照", fontsize=13, y=1.02)

    coverage_ax, score_ax = axes
    coverage_ax.bar(trend.index.astype(str), trend["policy_doc_count"].fillna(0), color="#7f7f7f")
    coverage_ax.set_title("Seed 政策文件覆盖")
    coverage_ax.set_xlabel("年份")
    coverage_ax.set_ylabel("城市—年份平均文件数")
    coverage_ax.tick_params(axis="x", rotation=0)

    if active_scores.empty:
        score_ax.text(0.5, 0.5, "暂无非缺失 seed 政策分数", ha="center", va="center", transform=score_ax.transAxes)
        score_ax.set_axis_off()
    else:
        latest_active_year = active_scores.index.max()
        latest_scores = active_scores.loc[latest_active_year, list(display_score_columns)].rename(display_score_columns)
        score_ax.barh(latest_scores.index.tolist(), latest_scores.values, color=["#4c78a8", "#f58518", "#54a24b"])
        score_ax.set_title(f"活跃 seed 分数（{latest_active_year}）")
        score_ax.set_xlabel("规则代理分数")
        score_ax.set_xlim(0, max(5.0, float(latest_scores.max()) * 1.15))
        for idx, value in enumerate(latest_scores.values):
            score_ax.text(value + 0.05, idx, f"{value:.2f}", va="center", fontsize=8.5)
    fig.text(
        0.01,
        -0.02,
        "注：当前仅为中央政策 seed 的规则代理分数，覆盖稀疏且不是已验证 LLM 趋势。",
        fontsize=8,
        color="#444444",
    )
    path = save_figure(fig, output_dir / "figure_04_policy_seed_mechanism_snapshot.pdf")
    return {
        "figure_id": "Figure 4",
        "filename": path.name,
        "caption_cn": "政策文本 seed 机制变量覆盖与分数快照（规则代理）",
        "caption_en": "Seed policy-text mechanism coverage and score snapshot (rule proxy)",
        "source": format_source(source_path),
        "status": "seed_rule_proxy_non_final",
        "caveat": "Seed central-document rule proxy only; sparse coverage snapshot, not a validated LLM trend.",
    }


def export_manifest(records: list[dict[str, object]], manifest_path: Path) -> Path:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([add_companion_raster_fields(record) for record in records]).to_csv(manifest_path, index=False)
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
        export_policy_seed_snapshot_figure(policy_panel, args.output_dir, args.policy_panel_path),
    ]
    manifest_path = export_manifest(records, args.manifest_path)
    print(f"Figures written to: {args.output_dir}")
    print(f"Figure manifest written to: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
