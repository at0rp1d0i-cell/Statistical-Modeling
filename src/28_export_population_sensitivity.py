import argparse
from pathlib import Path
from typing import Sequence

import pandas as pd

from stat_modeling.config import INTERIM_DATA_DIR
from stat_modeling.config import RANDOM_SEED
from stat_modeling.config import TABLES_DIR
from stat_modeling.config import ensure_project_directories
from stat_modeling.data.io import read_table
from stat_modeling.data.io import write_table
from stat_modeling.modeling.dml import fit_partial_linear_dml


DEFAULT_INPUT_PATH = INTERIM_DATA_DIR / "modeling" / "dml_candidate_input_2019_2023.csv"
DEFAULT_OUTPUT_CSV = TABLES_DIR / "table_11_population_sensitivity_robustness.csv"
DEFAULT_OUTPUT_TEX = TABLES_DIR / "table_11_population_sensitivity_robustness.tex"
DEFAULT_TREATMENT = "digital_inclusive_finance_index"
DEFAULT_OUTCOME = "co2_emission_intensity"
DEFAULT_BASE_CONTROLS = "gdp_total,secondary_industry_share,fiscal_expenditure"
DEFAULT_POPULATION_CONTROL = "population_control_candidate"

SPEC_LABELS_CN = {
    "baseline_no_population": "主规格：不含人口变量",
    "population_augmented": "敏感性：加入人口变量",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export DML population-control sensitivity robustness table.")
    parser.add_argument("--input-path", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-csv-path", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-tex-path", type=Path, default=DEFAULT_OUTPUT_TEX)
    parser.add_argument("--treatment-column", default=DEFAULT_TREATMENT)
    parser.add_argument("--outcome-column", default=DEFAULT_OUTCOME)
    parser.add_argument("--base-control-columns", default=DEFAULT_BASE_CONTROLS)
    parser.add_argument("--population-control-column", default=DEFAULT_POPULATION_CONTROL)
    parser.add_argument("--group-column", default="pku_city_code")
    parser.add_argument("--cluster-column", default="pku_city_code")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--random-seed", type=int, default=RANDOM_SEED)
    return parser


def parse_columns(raw_value: str) -> list[str]:
    return [value.strip() for value in raw_value.split(",") if value.strip()]


def require_columns(frame: pd.DataFrame, required: list[str], source: Path) -> None:
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"{source} missing required columns: {missing}")


def build_population_sensitivity_table(
    frame: pd.DataFrame,
    treatment_column: str,
    outcome_column: str,
    base_control_columns: list[str],
    population_control_column: str,
    group_column: str,
    cluster_column: str,
    folds: int,
    random_seed: int,
    source_path: Path,
) -> pd.DataFrame:
    require_columns(
        frame,
        [
            treatment_column,
            outcome_column,
            *base_control_columns,
            population_control_column,
            group_column,
            cluster_column,
        ],
        source_path,
    )
    specs = [
        ("baseline_no_population", base_control_columns),
        ("population_augmented", [*base_control_columns, population_control_column]),
    ]
    rows: list[dict[str, object]] = []
    for spec_key, controls in specs:
        result = fit_partial_linear_dml(
            frame=frame,
            outcome_column=outcome_column,
            treatment_column=treatment_column,
            control_columns=controls,
            folds=folds,
            random_seed=random_seed,
            group_column=group_column,
            cluster_column=cluster_column,
        )
        rows.append(
            {
                "model": "DML_population_sensitivity",
                "spec_key": spec_key,
                "spec_label_cn": SPEC_LABELS_CN[spec_key],
                "outcome_column": outcome_column,
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
                "control_columns": ", ".join(controls),
                "population_included": population_control_column in controls,
                "caveat": "Population control is a robustness/sensitivity check only and is not part of the main specification.",
            }
        )
    table = pd.DataFrame(rows)
    baseline_ate = float(table.loc[table["spec_key"] == "baseline_no_population", "ate"].iloc[0])
    table["ate_delta_vs_baseline"] = table["ate"].astype(float) - baseline_ate
    return table


def format_latex_table(table: pd.DataFrame) -> str:
    display = table[
        [
            "spec_label_cn",
            "ate",
            "std_error",
            "ci_lower",
            "ci_upper",
            "p_value",
            "ate_delta_vs_baseline",
            "nobs",
        ]
    ].copy()
    display.columns = [
        "规格",
        "ATE",
        "标准误",
        "95%CI下限",
        "95%CI上限",
        "P值",
        "相对主规格变化",
        "样本量",
    ]
    for column in ["ATE", "标准误", "95%CI下限", "95%CI上限", "P值", "相对主规格变化"]:
        display[column] = display[column].map(lambda value: f"{float(value):.4f}")
    display["样本量"] = display["样本量"].astype(int).astype(str)
    return display.to_latex(
        index=False,
        escape=False,
        caption="人口变量敏感性稳健性检验（DML，人口变量不进入主规格）",
        label="tab:population_sensitivity_robustness",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_project_directories()
    frame = read_table(args.input_path)
    table = build_population_sensitivity_table(
        frame=frame,
        treatment_column=args.treatment_column,
        outcome_column=args.outcome_column,
        base_control_columns=parse_columns(args.base_control_columns),
        population_control_column=args.population_control_column,
        group_column=args.group_column,
        cluster_column=args.cluster_column,
        folds=args.folds,
        random_seed=args.random_seed,
        source_path=args.input_path,
    )
    csv_path = write_table(table, args.output_csv_path)
    args.output_tex_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_tex_path.write_text(format_latex_table(table), encoding="utf-8")
    print(f"Population sensitivity CSV written to: {csv_path}")
    print(f"Population sensitivity LaTeX written to: {args.output_tex_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
