import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import pandas as pd
import statsmodels.formula.api as smf

from stat_modeling.config import INTERIM_DATA_DIR
from stat_modeling.config import TABLES_DIR
from stat_modeling.config import ensure_project_directories
from stat_modeling.data.io import read_table
from stat_modeling.data.io import write_table


DEFAULT_INPUT_PATH = INTERIM_DATA_DIR / "modeling" / "dml_candidate_input_2019_2023.csv"
DEFAULT_OUTPUT_CSV = TABLES_DIR / "table_06_ols_twfe_candidate.csv"
DEFAULT_OUTPUT_TEX = TABLES_DIR / "table_06_ols_twfe_candidate.tex"
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export candidate OLS two-way fixed effects robustness results."
    )
    parser.add_argument("--input-path", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-csv-path", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-tex-path", type=Path, default=DEFAULT_OUTPUT_TEX)
    parser.add_argument("--treatment-column", default=DEFAULT_TREATMENT)
    parser.add_argument("--outcome-columns", default=DEFAULT_OUTCOMES)
    parser.add_argument("--control-columns", default=DEFAULT_CONTROLS)
    parser.add_argument("--entity-column", default="pku_city_code")
    parser.add_argument("--time-column", default="year")
    parser.add_argument("--cluster-column", default="pku_city_code")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
