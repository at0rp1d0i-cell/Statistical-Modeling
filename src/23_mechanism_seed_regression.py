import argparse
from pathlib import Path
from typing import Sequence

from stat_modeling.config import INTERIM_DATA_DIR
from stat_modeling.config import TABLES_DIR
from stat_modeling.config import ensure_project_directories
from stat_modeling.data.io import read_table
from stat_modeling.data.io import write_table
from stat_modeling.data.io import write_text
from stat_modeling.data.mechanism_merge import merge_modeling_with_policy_seed
from stat_modeling.modeling.mechanism import fit_candidate_mechanism_ols


DEFAULT_INPUT = INTERIM_DATA_DIR / "modeling" / "dml_candidate_input_2019_2023.csv"
DEFAULT_POLICY = INTERIM_DATA_DIR / "policy_text" / "policy_mechanism_seed_panel_2019_2023.csv"
DEFAULT_OUTPUT = TABLES_DIR / "table_05_policy_seed_mechanism_candidate.csv"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run candidate mechanism regressions using seeded policy proxy variables.")
    parser.add_argument("--input-path", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--policy-seed-path", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--outcome-column", default="co2_emission_intensity")
    parser.add_argument("--treatment-column", default="digital_inclusive_finance_index")
    parser.add_argument("--cluster-column", default="pku_city_code")
    parser.add_argument(
        "--control-columns",
        default="gdp_total,secondary_industry_share,fiscal_expenditure",
        help="Comma-separated controls.",
    )
    parser.add_argument(
        "--mechanism-columns",
        default="sum_policy_strength_city_year,mean_execution_clarity_city_year,mean_digital_green_synergy_city_year",
        help="Comma-separated candidate mechanism columns.",
    )
    return parser


def parse_columns(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_project_directories()
    frame = read_table(args.input_path)
    policy_seed = read_table(args.policy_seed_path)
    frame = merge_modeling_with_policy_seed(frame, policy_seed)
    results = fit_candidate_mechanism_ols(
        frame=frame,
        outcome_column=args.outcome_column,
        treatment_column=args.treatment_column,
        mechanism_columns=parse_columns(args.mechanism_columns),
        control_columns=parse_columns(args.control_columns),
        cluster_column=args.cluster_column,
    )
    write_table(results, args.output_path)
    summary = "\n".join(
        [
            "Policy Seed Mechanism Candidate Summary",
            f"output: {args.output_path}",
            f"rows: {len(results)}",
            "boundary_note: these regressions use seeded central rule-proxy policy variables and should be treated as technical candidate evidence only.",
        ]
    ) + "\n"
    summary_path = write_text(summary, INTERIM_DATA_DIR / "policy_seed_mechanism_candidate_summary.txt")
    print(f"Candidate mechanism table written to: {args.output_path}")
    print(f"Summary written to: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
