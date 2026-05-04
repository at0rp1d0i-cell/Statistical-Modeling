import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import RandomForestRegressor

from stat_modeling.config import FIGURES_DIR
from stat_modeling.config import INTERIM_DATA_DIR
from stat_modeling.config import RANDOM_SEED
from stat_modeling.config import TABLES_DIR
from stat_modeling.config import ensure_project_directories
from stat_modeling.delivery.figure_formats import save_figure_with_rasters
from stat_modeling.delivery.figure_style import configure_paper_figure_style
from stat_modeling.data.io import read_table
from stat_modeling.data.io import write_table
from stat_modeling.modeling.dml import DMLResult
from stat_modeling.modeling.dml import fit_partial_linear_dml
from stat_modeling.modeling.dml import residualize_partial_linear_dml


DEFAULT_INPUT_PATH = INTERIM_DATA_DIR / "modeling" / "dml_candidate_input_2019_2023.csv"
DEFAULT_OUTPUT_CSV = TABLES_DIR / "table_06_ols_twfe_candidate.csv"
DEFAULT_OUTPUT_TEX = TABLES_DIR / "table_06_ols_twfe_candidate.tex"
DEFAULT_PLACEBO_SUMMARY_CSV = TABLES_DIR / "table_07_dml_placebo_candidate_summary.csv"
DEFAULT_PLACEBO_SUMMARY_TEX = TABLES_DIR / "table_07_dml_placebo_candidate_summary.tex"
DEFAULT_PLACEBO_DISTRIBUTION_CSV = TABLES_DIR / "table_07_dml_placebo_candidate_distribution.csv"
DEFAULT_PLACEBO_FIGURE = FIGURES_DIR / "figure_05_dml_placebo_distribution.pdf"
DEFAULT_LEARNER_CSV = TABLES_DIR / "table_08_dml_learner_replacement_candidate.csv"
DEFAULT_LEARNER_TEX = TABLES_DIR / "table_08_dml_learner_replacement_candidate.tex"
DEFAULT_TREATMENT = "digital_inclusive_finance_index"
DEFAULT_OUTCOMES = "co2_emission_intensity,co2_emission_total"
DEFAULT_CONTROLS = "gdp_total,secondary_industry_share,fiscal_expenditure"

OUTCOME_LABELS_CN = {
    "co2_emission_intensity": "碳排放强度",
    "co2_emission_total": "碳排放总量",
}

OUTCOME_LABELS_EN = {
    "co2_emission_intensity": "Carbon emission intensity",
    "co2_emission_total": "Total carbon emissions",
}


@dataclass(frozen=True)
class TwfeResult:
    outcome_column: str
    treatment_column: str
    coefficient: float
    std_error: float
    ci_lower: float
    ci_upper: float
    p_value: float
    nobs: int
    r_squared: float
    control_columns: list[str]
    entity_column: str
    time_column: str
    cluster_column: str

    def to_row(self) -> dict[str, object]:
        return {
            "model": "OLS_TWFE_candidate",
            "outcome_column": self.outcome_column,
            "outcome_label_cn": OUTCOME_LABELS_CN.get(self.outcome_column, self.outcome_column),
            "outcome_label_en": OUTCOME_LABELS_EN.get(self.outcome_column, self.outcome_column),
            "treatment_column": self.treatment_column,
            "coefficient": self.coefficient,
            "std_error": self.std_error,
            "ci_lower": self.ci_lower,
            "ci_upper": self.ci_upper,
            "p_value": self.p_value,
            "nobs": self.nobs,
            "r_squared": self.r_squared,
            "control_columns": ", ".join(self.control_columns),
            "city_fixed_effects": True,
            "year_fixed_effects": True,
            "entity_column": self.entity_column,
            "time_column": self.time_column,
            "cluster_column": self.cluster_column,
            "caveat": "Candidate robustness comparison only; does not replace the DML main specification.",
        }


@dataclass(frozen=True)
class PlaceboSummary:
    outcome_column: str
    treatment_column: str
    true_ate: float
    placebo_mean: float
    placebo_std: float
    placebo_q025: float
    placebo_median: float
    placebo_q975: float
    empirical_p_value: float
    permutations: int
    nobs: int
    folds: int
    split_strategy: str
    covariance_type: str
    control_columns: list[str]

    def to_row(self) -> dict[str, object]:
        return {
            "model": "DML_residual_permutation_placebo_candidate",
            "outcome_column": self.outcome_column,
            "outcome_label_cn": OUTCOME_LABELS_CN.get(self.outcome_column, self.outcome_column),
            "outcome_label_en": OUTCOME_LABELS_EN.get(self.outcome_column, self.outcome_column),
            "treatment_column": self.treatment_column,
            "true_ate": self.true_ate,
            "placebo_mean": self.placebo_mean,
            "placebo_std": self.placebo_std,
            "placebo_q025": self.placebo_q025,
            "placebo_median": self.placebo_median,
            "placebo_q975": self.placebo_q975,
            "empirical_p_value": self.empirical_p_value,
            "permutations": self.permutations,
            "nobs": self.nobs,
            "folds": self.folds,
            "split_strategy": self.split_strategy,
            "covariance_type": self.covariance_type,
            "control_columns": ", ".join(self.control_columns),
            "caveat": (
                "Candidate residual-permutation placebo only; final robustness should rerun after "
                "sample and specification lock."
            ),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export candidate OLS TWFE and DML placebo robustness results."
    )
    parser.add_argument("--input-path", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-csv-path", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-tex-path", type=Path, default=DEFAULT_OUTPUT_TEX)
    parser.add_argument("--placebo-summary-csv-path", type=Path, default=DEFAULT_PLACEBO_SUMMARY_CSV)
    parser.add_argument("--placebo-summary-tex-path", type=Path, default=DEFAULT_PLACEBO_SUMMARY_TEX)
    parser.add_argument("--placebo-distribution-csv-path", type=Path, default=DEFAULT_PLACEBO_DISTRIBUTION_CSV)
    parser.add_argument("--placebo-figure-path", type=Path, default=DEFAULT_PLACEBO_FIGURE)
    parser.add_argument("--learner-csv-path", type=Path, default=DEFAULT_LEARNER_CSV)
    parser.add_argument("--learner-tex-path", type=Path, default=DEFAULT_LEARNER_TEX)
    parser.add_argument("--treatment-column", default=DEFAULT_TREATMENT)
    parser.add_argument("--outcome-columns", default=DEFAULT_OUTCOMES)
    parser.add_argument("--placebo-outcome-column", default="co2_emission_intensity")
    parser.add_argument("--learner-outcome-column", default="co2_emission_intensity")
    parser.add_argument("--control-columns", default=DEFAULT_CONTROLS)
    parser.add_argument("--entity-column", default="pku_city_code")
    parser.add_argument("--time-column", default="year")
    parser.add_argument("--cluster-column", default="pku_city_code")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--placebo-permutations", type=int, default=500)
    parser.add_argument("--random-seed", type=int, default=RANDOM_SEED)
    return parser


def parse_columns(raw_value: str) -> list[str]:
    return [value.strip() for value in raw_value.split(",") if value.strip()]


def require_columns(frame: pd.DataFrame, required_columns: list[str], source: Path) -> None:
    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{source} missing required columns: {missing}")


def build_formula(
    outcome_column: str,
    treatment_column: str,
    control_columns: list[str],
    entity_column: str,
    time_column: str,
) -> str:
    rhs_terms = [treatment_column, *control_columns, f"C({entity_column})", f"C({time_column})"]
    return f"{outcome_column} ~ {' + '.join(rhs_terms)}"


def fit_ols_twfe(
    frame: pd.DataFrame,
    outcome_column: str,
    treatment_column: str,
    control_columns: list[str],
    entity_column: str,
    time_column: str,
    cluster_column: str,
) -> TwfeResult:
    required = list(
        dict.fromkeys([outcome_column, treatment_column, *control_columns, entity_column, time_column, cluster_column])
    )
    working = frame[required].dropna().copy()
    if working.empty:
        raise ValueError(f"No complete observations for OLS TWFE outcome: {outcome_column}")
    if working[entity_column].nunique() < 2:
        raise ValueError("OLS TWFE requires at least two entities")
    if working[time_column].nunique() < 2:
        raise ValueError("OLS TWFE requires at least two time periods")

    formula = build_formula(outcome_column, treatment_column, control_columns, entity_column, time_column)
    fitted = smf.ols(formula=formula, data=working).fit(
        cov_type="cluster",
        cov_kwds={"groups": working[cluster_column]},
    )
    interval = fitted.conf_int().loc[treatment_column]
    return TwfeResult(
        outcome_column=outcome_column,
        treatment_column=treatment_column,
        coefficient=float(fitted.params[treatment_column]),
        std_error=float(fitted.bse[treatment_column]),
        ci_lower=float(interval.iloc[0]),
        ci_upper=float(interval.iloc[1]),
        p_value=float(fitted.pvalues[treatment_column]),
        nobs=int(fitted.nobs),
        r_squared=float(fitted.rsquared),
        control_columns=control_columns,
        entity_column=entity_column,
        time_column=time_column,
        cluster_column=cluster_column,
    )


def build_ols_twfe_table(
    frame: pd.DataFrame,
    outcome_columns: list[str],
    treatment_column: str,
    control_columns: list[str],
    entity_column: str,
    time_column: str,
    cluster_column: str,
    source_path: Path,
) -> pd.DataFrame:
    required = [
        *outcome_columns,
        treatment_column,
        *control_columns,
        entity_column,
        time_column,
        cluster_column,
    ]
    require_columns(frame, list(dict.fromkeys(required)), source_path)
    rows = [
        fit_ols_twfe(
            frame=frame,
            outcome_column=outcome,
            treatment_column=treatment_column,
            control_columns=control_columns,
            entity_column=entity_column,
            time_column=time_column,
            cluster_column=cluster_column,
        ).to_row()
        for outcome in outcome_columns
    ]
    return pd.DataFrame(rows)


def format_latex_table(table: pd.DataFrame) -> str:
    display = table[
        [
            "outcome_label_cn",
            "coefficient",
            "std_error",
            "ci_lower",
            "ci_upper",
            "p_value",
            "nobs",
            "r_squared",
        ]
    ].copy()
    display.columns = [
        "结果变量",
        "TWFE系数",
        "聚类标准误",
        "95%CI下限",
        "95%CI上限",
        "P值",
        "样本量",
        "R²",
    ]
    for column in ["TWFE系数", "聚类标准误", "95%CI下限", "95%CI上限", "P值", "R²"]:
        display[column] = display[column].map(lambda value: f"{value:.4f}")
    display["样本量"] = display["样本量"].astype(int).astype(str)
    return display.to_latex(
        index=False,
        escape=False,
        caption="OLS 双向固定效应候选稳健性对照（城市与年份固定效应，城市聚类标准误）",
        label="tab:ols_twfe_candidate",
    )


def export_ols_twfe_table(table: pd.DataFrame, output_csv_path: Path, output_tex_path: Path) -> dict[str, Path]:
    csv_path = write_table(table, output_csv_path)
    output_tex_path.parent.mkdir(parents=True, exist_ok=True)
    output_tex_path.write_text(format_latex_table(table), encoding="utf-8")
    return {"csv_path": csv_path, "tex_path": output_tex_path}


def run_dml_residual_placebo(
    frame: pd.DataFrame,
    outcome_column: str,
    treatment_column: str,
    control_columns: list[str],
    group_column: str,
    cluster_column: str,
    folds: int,
    permutations: int,
    random_seed: int,
) -> tuple[DMLResult, PlaceboSummary, pd.DataFrame]:
    if permutations <= 0:
        raise ValueError("placebo_permutations must be positive")
    true_result = fit_partial_linear_dml(
        frame=frame,
        outcome_column=outcome_column,
        treatment_column=treatment_column,
        control_columns=control_columns,
        folds=folds,
        random_seed=random_seed,
        group_column=group_column,
        cluster_column=cluster_column,
    )
    residuals = residualize_partial_linear_dml(
        frame=frame,
        outcome_column=outcome_column,
        treatment_column=treatment_column,
        control_columns=control_columns,
        folds=folds,
        random_seed=random_seed,
        group_column=group_column,
        cluster_column=cluster_column,
    )
    clusters = residuals.model_frame[cluster_column].to_numpy()
    rng = np.random.default_rng(random_seed)
    rows: list[dict[str, object]] = []
    for iteration in range(1, permutations + 1):
        placebo_t = rng.permutation(residuals.t_res)
        fitted = sm.OLS(residuals.y_res, sm.add_constant(placebo_t)).fit(
            cov_type="cluster",
            cov_kwds={"groups": clusters},
        )
        rows.append(
            {
                "iteration": iteration,
                "placebo_ate": float(fitted.params[1]),
                "placebo_std_error": float(fitted.bse[1]),
                "placebo_p_value": float(fitted.pvalues[1]),
            }
        )
    distribution = pd.DataFrame(rows)
    abs_true = abs(true_result.ate)
    extreme_count = int((distribution["placebo_ate"].abs() >= abs_true).sum())
    empirical_p_value = (extreme_count + 1) / (permutations + 1)
    summary = PlaceboSummary(
        outcome_column=outcome_column,
        treatment_column=treatment_column,
        true_ate=true_result.ate,
        placebo_mean=float(distribution["placebo_ate"].mean()),
        placebo_std=float(distribution["placebo_ate"].std()),
        placebo_q025=float(distribution["placebo_ate"].quantile(0.025)),
        placebo_median=float(distribution["placebo_ate"].quantile(0.5)),
        placebo_q975=float(distribution["placebo_ate"].quantile(0.975)),
        empirical_p_value=float(empirical_p_value),
        permutations=permutations,
        nobs=true_result.nobs,
        folds=true_result.folds,
        split_strategy=true_result.split_strategy,
        covariance_type=true_result.covariance_type,
        control_columns=control_columns,
    )
    distribution["true_ate"] = true_result.ate
    distribution["outcome_column"] = outcome_column
    distribution["treatment_column"] = treatment_column
    return true_result, summary, distribution


def format_placebo_summary_latex(summary_table: pd.DataFrame) -> str:
    display = summary_table[
        [
            "outcome_label_cn",
            "true_ate",
            "placebo_mean",
            "placebo_std",
            "placebo_q025",
            "placebo_q975",
            "empirical_p_value",
            "permutations",
            "nobs",
        ]
    ].copy()
    display.columns = [
        "结果变量",
        "真实ATE",
        "Placebo均值",
        "Placebo标准差",
        "Placebo 2.5%",
        "Placebo 97.5%",
        "经验P值",
        "置换次数",
        "样本量",
    ]
    for column in ["真实ATE", "Placebo均值", "Placebo标准差", "Placebo 2.5%", "Placebo 97.5%", "经验P值"]:
        display[column] = display[column].map(lambda value: f"{value:.4f}")
    for column in ["置换次数", "样本量"]:
        display[column] = display[column].astype(int).astype(str)
    return display.to_latex(
        index=False,
        escape=False,
        caption="DML 残差置换安慰剂检验候选结果",
        label="tab:dml_placebo_candidate",
    )


def save_placebo_figure(distribution: pd.DataFrame, summary: PlaceboSummary, output_path: Path) -> Path:
    configure_paper_figure_style()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.hist(distribution["placebo_ate"], bins=30, color="#9e9e9e", edgecolor="white")
    ax.axvline(summary.true_ate, color="#2f5597", linestyle="-", linewidth=1.8, label=f"真实 ATE = {summary.true_ate:.4f}")
    ax.axvline(-abs(summary.true_ate), color="#2f5597", linestyle=":", linewidth=1.2, label="|真实 ATE| 阈值")
    ax.axvline(abs(summary.true_ate), color="#2f5597", linestyle=":", linewidth=1.2)
    ax.axvline(0, color="#444444", linestyle="--", linewidth=1)
    ax.set_title("DML 残差置换安慰剂检验分布")
    ax.set_xlabel("安慰剂 ATE")
    ax.set_ylabel("频数")
    ax.text(
        0.98,
        0.95,
        f"置换 p 值 = {summary.empirical_p_value:.4f}\n置换次数 = {summary.permutations}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#dddddd", "alpha": 0.9},
    )
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    save_figure_with_rasters(fig, output_path)
    plt.close(fig)
    return output_path


def export_placebo_outputs(
    summary: PlaceboSummary,
    distribution: pd.DataFrame,
    summary_csv_path: Path,
    summary_tex_path: Path,
    distribution_csv_path: Path,
    figure_path: Path,
) -> dict[str, Path]:
    summary_table = pd.DataFrame([summary.to_row()])
    summary_csv = write_table(summary_table, summary_csv_path)
    summary_tex_path.parent.mkdir(parents=True, exist_ok=True)
    summary_tex_path.write_text(format_placebo_summary_latex(summary_table), encoding="utf-8")
    distribution_csv = write_table(distribution, distribution_csv_path)
    figure = save_placebo_figure(distribution, summary, figure_path)
    return {
        "summary_csv_path": summary_csv,
        "summary_tex_path": summary_tex_path,
        "distribution_csv_path": distribution_csv,
        "figure_path": figure,
    }


def build_learner_specs(random_seed: int) -> list[tuple[str, object]]:
    return [
        ("GradientBoosting baseline", GradientBoostingRegressor(random_state=random_seed)),
        (
            "RandomForest replacement",
            RandomForestRegressor(
                n_estimators=100,
                min_samples_leaf=5,
                random_state=random_seed,
                n_jobs=-1,
            ),
        ),
        (
            "ExtraTrees replacement",
            ExtraTreesRegressor(
                n_estimators=100,
                min_samples_leaf=5,
                random_state=random_seed,
                n_jobs=-1,
            ),
        ),
    ]


def build_learner_replacement_table(
    frame: pd.DataFrame,
    outcome_column: str,
    treatment_column: str,
    control_columns: list[str],
    group_column: str,
    cluster_column: str,
    folds: int,
    random_seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for learner_label, learner_model in build_learner_specs(random_seed):
        result = fit_partial_linear_dml(
            frame=frame,
            outcome_column=outcome_column,
            treatment_column=treatment_column,
            control_columns=control_columns,
            folds=folds,
            random_seed=random_seed,
            group_column=group_column,
            cluster_column=cluster_column,
            model_y=learner_model,
            model_t=learner_model,
        )
        rows.append(
            {
                "model": "DML_learner_replacement_candidate",
                "learner_label": learner_label,
                "outcome_column": outcome_column,
                "outcome_label_cn": OUTCOME_LABELS_CN.get(outcome_column, outcome_column),
                "outcome_label_en": OUTCOME_LABELS_EN.get(outcome_column, outcome_column),
                "treatment_column": treatment_column,
                "ate": result.ate,
                "std_error": result.std_error,
                "ci_lower": result.ci_lower,
                "ci_upper": result.ci_upper,
                "p_value": result.p_value,
                "nobs": result.nobs,
                "folds": result.folds,
                "split_strategy": result.split_strategy,
                "covariance_type": result.covariance_type,
                "nuisance_model_y": result.nuisance_model_y,
                "nuisance_model_t": result.nuisance_model_t,
                "control_columns": ", ".join(control_columns),
                "caveat": "Candidate learner-replacement robustness only; rerun after final specification lock.",
            }
        )
    return pd.DataFrame(rows)


def format_learner_replacement_latex(table: pd.DataFrame) -> str:
    display = table[
        [
            "learner_label",
            "ate",
            "std_error",
            "ci_lower",
            "ci_upper",
            "p_value",
            "nobs",
        ]
    ].copy()
    display.columns = [
        "学习器",
        "ATE",
        "标准误",
        "95%CI下限",
        "95%CI上限",
        "P值",
        "样本量",
    ]
    for column in ["ATE", "标准误", "95%CI下限", "95%CI上限", "P值"]:
        display[column] = display[column].map(lambda value: f"{value:.4f}")
    display["样本量"] = display["样本量"].astype(int).astype(str)
    return display.to_latex(
        index=False,
        escape=False,
        caption="DML 学习器替换候选稳健性检验",
        label="tab:dml_learner_replacement_candidate",
    )


def export_learner_replacement_table(table: pd.DataFrame, output_csv_path: Path, output_tex_path: Path) -> dict[str, Path]:
    csv_path = write_table(table, output_csv_path)
    output_tex_path.parent.mkdir(parents=True, exist_ok=True)
    output_tex_path.write_text(format_learner_replacement_latex(table), encoding="utf-8")
    return {"csv_path": csv_path, "tex_path": output_tex_path}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_project_directories()
    frame = read_table(args.input_path)
    outcome_columns = parse_columns(args.outcome_columns)
    control_columns = parse_columns(args.control_columns)
    table = build_ols_twfe_table(
        frame=frame,
        outcome_columns=outcome_columns,
        treatment_column=args.treatment_column,
        control_columns=control_columns,
        entity_column=args.entity_column,
        time_column=args.time_column,
        cluster_column=args.cluster_column,
        source_path=args.input_path,
    )
    outputs = export_ols_twfe_table(table, args.output_csv_path, args.output_tex_path)
    print(f"CSV table written to: {outputs['csv_path']}")
    print(f"LaTeX table written to: {outputs['tex_path']}")
    print("Boundary note: OLS TWFE is a candidate robustness comparison and does not replace DML.")
    _, placebo_summary, placebo_distribution = run_dml_residual_placebo(
        frame=frame,
        outcome_column=args.placebo_outcome_column,
        treatment_column=args.treatment_column,
        control_columns=control_columns,
        group_column=args.entity_column,
        cluster_column=args.cluster_column,
        folds=args.folds,
        permutations=args.placebo_permutations,
        random_seed=args.random_seed,
    )
    placebo_outputs = export_placebo_outputs(
        summary=placebo_summary,
        distribution=placebo_distribution,
        summary_csv_path=args.placebo_summary_csv_path,
        summary_tex_path=args.placebo_summary_tex_path,
        distribution_csv_path=args.placebo_distribution_csv_path,
        figure_path=args.placebo_figure_path,
    )
    print(f"Placebo summary CSV written to: {placebo_outputs['summary_csv_path']}")
    print(f"Placebo summary LaTeX written to: {placebo_outputs['summary_tex_path']}")
    print(f"Placebo distribution written to: {placebo_outputs['distribution_csv_path']}")
    print(f"Placebo figure written to: {placebo_outputs['figure_path']}")
    print("Boundary note: placebo output is candidate evidence until final sample/specification lock.")
    learner_table = build_learner_replacement_table(
        frame=frame,
        outcome_column=args.learner_outcome_column,
        treatment_column=args.treatment_column,
        control_columns=control_columns,
        group_column=args.entity_column,
        cluster_column=args.cluster_column,
        folds=args.folds,
        random_seed=args.random_seed,
    )
    learner_outputs = export_learner_replacement_table(
        learner_table,
        args.learner_csv_path,
        args.learner_tex_path,
    )
    print(f"Learner replacement CSV written to: {learner_outputs['csv_path']}")
    print(f"Learner replacement LaTeX written to: {learner_outputs['tex_path']}")
    print("Boundary note: learner replacement output is candidate evidence until final specification lock.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
