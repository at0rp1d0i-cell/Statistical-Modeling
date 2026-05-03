"""Export paper-supporting materials that strengthen the evidence narrative.

The outputs in this script are deliberately descriptive or synthesis-oriented. They
help reviewers understand sample construction, variable relationships, regional
patterns, and the robustness evidence ladder without changing the approved main
DML specification.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

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


DEFAULT_MODELING_PANEL = INTERIM_DATA_DIR / "modeling" / "modeling_candidate_panel_2019_2023.csv"
DEFAULT_DML_INPUT = INTERIM_DATA_DIR / "modeling" / "dml_candidate_input_2019_2023.csv"
DEFAULT_CATE_GROUPS = INTERIM_DATA_DIR / "modeling" / "heterogeneity_candidate_cate_with_groups.csv"
DEFAULT_TABLE_02 = TABLES_DIR / "table_02_dml_main_and_robustness.csv"
DEFAULT_TABLE_06 = TABLES_DIR / "table_06_ols_twfe_candidate.csv"
DEFAULT_TABLE_08 = TABLES_DIR / "table_08_dml_learner_replacement_candidate.csv"
DEFAULT_TABLE_11 = TABLES_DIR / "table_11_population_sensitivity_robustness.csv"

DEFAULT_TABLE_14_CSV = TABLES_DIR / "table_14_sample_construction_coverage.csv"
DEFAULT_TABLE_14_TEX = TABLES_DIR / "table_14_sample_construction_coverage.tex"
DEFAULT_TABLE_15_CSV = TABLES_DIR / "table_15_variable_correlation_matrix.csv"
DEFAULT_TABLE_15_TEX = TABLES_DIR / "table_15_variable_correlation_matrix.tex"

CORRELATION_VARIABLES = {
    "co2_emission_intensity": "Carbon intensity",
    "co2_emission_total": "Total emissions",
    "digital_inclusive_finance_index": "Digital finance",
    "dfi_coverage_breadth": "Coverage breadth",
    "dfi_usage_depth": "Usage depth",
    "dfi_digitization_level": "Digitization level",
    "gdp_total": "GDP",
    "secondary_industry_share": "Secondary industry",
    "fiscal_expenditure": "Fiscal expenditure",
    "population_control_candidate": "Population candidate",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export additional paper support tables and figures.")
    parser.add_argument("--modeling-panel-path", type=Path, default=DEFAULT_MODELING_PANEL)
    parser.add_argument("--dml-input-path", type=Path, default=DEFAULT_DML_INPUT)
    parser.add_argument("--cate-groups-path", type=Path, default=DEFAULT_CATE_GROUPS)
    parser.add_argument("--table-02-path", type=Path, default=DEFAULT_TABLE_02)
    parser.add_argument("--table-06-path", type=Path, default=DEFAULT_TABLE_06)
    parser.add_argument("--table-08-path", type=Path, default=DEFAULT_TABLE_08)
    parser.add_argument("--table-11-path", type=Path, default=DEFAULT_TABLE_11)
    parser.add_argument("--tables-dir", type=Path, default=TABLES_DIR)
    parser.add_argument("--figures-dir", type=Path, default=FIGURES_DIR)
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


def require_columns(frame: pd.DataFrame, required_columns: Iterable[str], source: Path) -> None:
    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{source} missing required columns: {missing}")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def write_csv_and_tex(table: pd.DataFrame, csv_path: Path, tex_path: Path, caption: str, label: str) -> dict[str, Path]:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(csv_path, index=False)
    tex_path.write_text(table.to_latex(index=False, escape=False, caption=caption, label=label), encoding="utf-8")
    return {"csv": csv_path, "tex": tex_path}


def summarize_stage(frame: pd.DataFrame, stage_order: int, stage_cn: str, source: str, note: str) -> dict[str, object]:
    require_columns(frame, ["year", "pku_city_code"], Path(source))
    years = sorted(pd.to_numeric(frame["year"], errors="coerce").dropna().astype(int).unique().tolist())
    return {
        "stage_order": stage_order,
        "stage_cn": stage_cn,
        "source": source,
        "city_year_obs": int(len(frame)),
        "cities": int(frame["pku_city_code"].nunique()),
        "year_range": f"{min(years)}-{max(years)}" if years else "",
        "note": note,
    }


def build_sample_construction_table(modeling_panel: pd.DataFrame, dml_input: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        modeling_panel,
        ["year", "pku_city_code", "has_cmcc_outcome", "has_core_controls", "ready_for_dml_candidate"],
        DEFAULT_MODELING_PANEL,
    )
    has_cmcc = modeling_panel["has_cmcc_outcome"].astype(bool)
    has_core_controls = modeling_panel["has_core_controls"].astype(bool)
    ready_for_dml = modeling_panel["ready_for_dml_candidate"].astype(bool)
    stage_2 = modeling_panel.loc[has_cmcc].copy()
    stage_3 = modeling_panel.loc[has_cmcc & has_core_controls].copy()
    stage_4 = modeling_panel.loc[has_cmcc & has_core_controls & ready_for_dml].copy()
    stages = [
        summarize_stage(
            modeling_panel,
            1,
            "PKU-CMCC 候选匹配面板",
            "modeling_candidate_panel_2019_2023.csv",
            "数字普惠金融与碳排放候选合并后的城市—年份面板。",
        ),
        summarize_stage(
            stage_2,
            2,
            "具备 CMCC 碳排放结果变量",
            "modeling_candidate_panel_2019_2023.csv",
            "保留具有城市碳排放总量的观测。",
        ),
        summarize_stage(
            stage_3,
            3,
            "同时具备核心控制变量",
            "modeling_candidate_panel_2019_2023.csv",
            "在具备结果变量基础上保留 GDP、第二产业占比和财政支出可用观测。",
        ),
        summarize_stage(
            stage_4,
            4,
            "DML 候选就绪样本",
            "modeling_candidate_panel_2019_2023.csv",
            "同时满足结果变量、处理变量和核心控制变量可用。",
        ),
        summarize_stage(
            dml_input,
            5,
            "最终 DML 输入样本",
            "dml_candidate_input_2019_2023.csv",
            "进入当前主回归、稳健性和异质性分析的样本。",
        ),
    ]
    table = pd.DataFrame(stages)
    table["retention_vs_stage_1"] = (table["city_year_obs"] / table.loc[0, "city_year_obs"]).round(4)
    table["retention_vs_previous"] = (table["city_year_obs"] / table["city_year_obs"].shift(1)).round(4)
    table.loc[0, "retention_vs_previous"] = 1.0
    return table[
        [
            "stage_order",
            "stage_cn",
            "city_year_obs",
            "cities",
            "year_range",
            "retention_vs_stage_1",
            "retention_vs_previous",
            "note",
        ]
    ]


def build_correlation_matrix(dml_input: pd.DataFrame) -> pd.DataFrame:
    require_columns(dml_input, CORRELATION_VARIABLES.keys(), DEFAULT_DML_INPUT)
    numeric = dml_input[list(CORRELATION_VARIABLES)].apply(pd.to_numeric, errors="coerce")
    corr = numeric.corr().round(3)
    corr.index = [CORRELATION_VARIABLES[column] for column in corr.index]
    corr.columns = [CORRELATION_VARIABLES[column] for column in corr.columns]
    return corr.reset_index(names="Variable")


def save_figure(fig: plt.Figure, output_path: Path) -> dict[str, Path]:
    outputs = save_figure_with_rasters(fig, output_path)
    plt.close(fig)
    return outputs


def export_sample_coverage_figure(dml_input: pd.DataFrame, output_dir: Path) -> dict[str, Path]:
    require_columns(dml_input, ["year", "pku_city_code"], DEFAULT_DML_INPUT)
    coverage = (
        dml_input.groupby("year")
        .agg(city_year_obs=("pku_city_code", "size"), cities=("pku_city_code", "nunique"))
        .reset_index()
        .sort_values("year")
    )
    fig, axes = plt.subplots(ncols=2, figsize=(8.6, 3.8))
    fig.suptitle("DML sample coverage by year", fontsize=13)
    axes[0].bar(coverage["year"].astype(str), coverage["city_year_obs"], color="#6b6b6b")
    axes[0].set_title("City-year observations")
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Obs.")
    axes[1].bar(coverage["year"].astype(str), coverage["cities"], color="#2f5597")
    axes[1].set_title("Cities covered")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Cities")
    return save_figure(fig, output_dir / "figure_07_sample_coverage_by_year.pdf")


def build_robustness_rows(
    table_02: pd.DataFrame,
    table_06: pd.DataFrame,
    table_08: pd.DataFrame,
    table_11: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    main = table_02.loc[table_02["outcome_column"] == "co2_emission_intensity"].head(1)
    if not main.empty:
        row = main.iloc[0]
        rows.append(
            {
                "label": "DML main",
                "estimate": row["ate"],
                "ci_lower": row["ci_lower"],
                "ci_upper": row["ci_upper"],
                "p_value": row["p_value"],
                "family": "Main",
            }
        )
    ols = table_06.loc[table_06["outcome_column"] == "co2_emission_intensity"].head(1)
    if not ols.empty:
        row = ols.iloc[0]
        rows.append(
            {
                "label": "OLS TWFE",
                "estimate": row["coefficient"],
                "ci_lower": row["ci_lower"],
                "ci_upper": row["ci_upper"],
                "p_value": row["p_value"],
                "family": "Benchmark",
            }
        )
    for _, row in table_08.iterrows():
        rows.append(
            {
                "label": str(row["learner_label"]).replace(" replacement", ""),
                "estimate": row["ate"],
                "ci_lower": row["ci_lower"],
                "ci_upper": row["ci_upper"],
                "p_value": row["p_value"],
                "family": "Learner",
            }
        )
    pop = table_11.loc[table_11["spec_key"] == "population_augmented"].head(1)
    if not pop.empty:
        row = pop.iloc[0]
        rows.append(
            {
                "label": "DML + population",
                "estimate": row["ate"],
                "ci_lower": row["ci_lower"],
                "ci_upper": row["ci_upper"],
                "p_value": row["p_value"],
                "family": "Sensitivity",
            }
        )
    robustness = pd.DataFrame(rows)
    if robustness.empty:
        raise ValueError("No robustness rows available for Figure 8")
    for column in ["estimate", "ci_lower", "ci_upper", "p_value"]:
        robustness[column] = pd.to_numeric(robustness[column], errors="coerce")
    return robustness.dropna(subset=["estimate", "ci_lower", "ci_upper"])


def export_robustness_forest_figure(robustness: pd.DataFrame, output_dir: Path) -> dict[str, Path]:
    ordered = robustness.iloc[::-1].reset_index(drop=True)
    y = range(len(ordered))
    colors = ordered["family"].map(
        {"Main": "#2f5597", "Benchmark": "#7f7f7f", "Learner": "#5b9bd5", "Sensitivity": "#c00000"}
    ).fillna("#666666")
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.axvline(0, color="#444444", linestyle="--", linewidth=1)
    for idx, row in ordered.iterrows():
        estimate = row["estimate"]
        ax.errorbar(
            estimate,
            idx,
            xerr=[[estimate - row["ci_lower"]], [row["ci_upper"] - estimate]],
            fmt="o",
            color=colors.iloc[idx],
            ecolor=colors.iloc[idx],
            capsize=3,
        )
        ax.text(row["ci_upper"] + 0.003, idx, f"p={row['p_value']:.3f}", va="center", fontsize=8)
    ax.set_yticks(list(y), ordered["label"].tolist())
    ax.set_xlabel("Effect on carbon emission intensity")
    ax.set_title("Robustness evidence ladder: intensity-scale estimates")
    ax.grid(axis="x", alpha=0.25)
    return save_figure(fig, output_dir / "figure_08_robustness_evidence_forest.pdf")


def export_regional_trend_figure(dml_input: pd.DataFrame, cate_groups: pd.DataFrame, output_dir: Path) -> dict[str, Path]:
    require_columns(dml_input, ["year", "pku_city_code", "digital_inclusive_finance_index", "co2_emission_intensity"], DEFAULT_DML_INPUT)
    require_columns(cate_groups, ["pku_city_code", "region_group_cn"], DEFAULT_CATE_GROUPS)
    city_region = cate_groups[["pku_city_code", "region_group_cn"]].drop_duplicates("pku_city_code")
    merged = dml_input.merge(city_region, on="pku_city_code", how="left")
    region_label_map = {"东部": "East", "中部": "Central", "西部": "West", "东北": "Northeast"}
    merged["region_group_label"] = merged["region_group_cn"].map(region_label_map).fillna("Unclassified")
    trend = (
        merged.groupby(["year", "region_group_label"])[["digital_inclusive_finance_index", "co2_emission_intensity"]]
        .mean()
        .reset_index()
        .sort_values(["region_group_label", "year"])
    )
    fig, axes = plt.subplots(ncols=2, figsize=(10.0, 4.0), sharex=True)
    for region, group in trend.groupby("region_group_label"):
        axes[0].plot(group["year"], group["digital_inclusive_finance_index"], marker="o", linewidth=1.4, label=region)
        axes[1].plot(group["year"], group["co2_emission_intensity"], marker="s", linewidth=1.4, label=region)
    axes[0].set_title("Digital finance by region")
    axes[0].set_ylabel("Mean index")
    axes[1].set_title("Carbon intensity by region")
    axes[1].set_ylabel("Mean intensity")
    for ax in axes:
        ax.set_xlabel("Year")
        ax.set_xticks(sorted(trend["year"].unique().tolist()))
    axes[1].legend(frameon=False, fontsize=8, loc="best")
    fig.suptitle("Regional descriptive trends", fontsize=13)
    return save_figure(fig, output_dir / "figure_09_regional_descriptive_trends.pdf")


def export_support_materials(
    modeling_panel_path: Path,
    dml_input_path: Path,
    cate_groups_path: Path,
    table_02_path: Path,
    table_06_path: Path,
    table_08_path: Path,
    table_11_path: Path,
    tables_dir: Path,
    figures_dir: Path,
) -> dict[str, Path]:
    configure_style()
    modeling_panel = read_csv(modeling_panel_path)
    dml_input = read_csv(dml_input_path)
    cate_groups = read_csv(cate_groups_path)
    table_02 = read_csv(table_02_path)
    table_06 = read_csv(table_06_path)
    table_08 = read_csv(table_08_path)
    table_11 = read_csv(table_11_path)

    table_14 = build_sample_construction_table(modeling_panel, dml_input)
    table_15 = build_correlation_matrix(dml_input)
    outputs = {}
    outputs.update(
        {
            f"sample_{key}": value
            for key, value in write_csv_and_tex(
                table_14,
                tables_dir / DEFAULT_TABLE_14_CSV.name,
                tables_dir / DEFAULT_TABLE_14_TEX.name,
                caption="样本构造与覆盖情况",
                label="tab:sample_construction_coverage",
            ).items()
        }
    )
    outputs.update(
        {
            f"correlation_{key}": value
            for key, value in write_csv_and_tex(
                table_15,
                tables_dir / DEFAULT_TABLE_15_CSV.name,
                tables_dir / DEFAULT_TABLE_15_TEX.name,
                caption="主要变量相关系数矩阵",
                label="tab:variable_correlation_matrix",
            ).items()
        }
    )
    outputs.update({f"coverage_{key}": value for key, value in export_sample_coverage_figure(dml_input, figures_dir).items()})
    robustness = build_robustness_rows(table_02, table_06, table_08, table_11)
    outputs.update({f"forest_{key}": value for key, value in export_robustness_forest_figure(robustness, figures_dir).items()})
    outputs.update({f"regional_{key}": value for key, value in export_regional_trend_figure(dml_input, cate_groups, figures_dir).items()})
    return outputs


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ensure_project_directories()
    outputs = export_support_materials(
        modeling_panel_path=args.modeling_panel_path,
        dml_input_path=args.dml_input_path,
        cate_groups_path=args.cate_groups_path,
        table_02_path=args.table_02_path,
        table_06_path=args.table_06_path,
        table_08_path=args.table_08_path,
        table_11_path=args.table_11_path,
        tables_dir=args.tables_dir,
        figures_dir=args.figures_dir,
    )
    for label, path in sorted(outputs.items()):
        print(f"{label}: {path}")
    print("Boundary note: These materials support interpretation and review; they do not change the approved main DML specification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
