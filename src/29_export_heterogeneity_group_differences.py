import argparse
from pathlib import Path
from typing import Sequence

import pandas as pd

from stat_modeling.config import INTERIM_DATA_DIR
from stat_modeling.config import RANDOM_SEED
from stat_modeling.config import TABLES_DIR
from stat_modeling.config import ensure_project_directories
from stat_modeling.data.io import write_table
from stat_modeling.modeling.heterogeneity_groups import build_heterogeneity_group_summary
from stat_modeling.modeling.heterogeneity_groups import build_pairwise_group_differences


DEFAULT_CATE_WITH_GROUPS_PATH = INTERIM_DATA_DIR / "modeling" / "heterogeneity_candidate_cate_with_groups.csv"
DEFAULT_CATE_PATH = INTERIM_DATA_DIR / "modeling" / "heterogeneity_candidate_cate.csv"
DEFAULT_MODEL_INPUT_PATH = INTERIM_DATA_DIR / "modeling" / "dml_candidate_input_2019_2023.csv"
DEFAULT_OUTPUT_CSV = TABLES_DIR / "table_12_heterogeneity_group_differences.csv"
DEFAULT_OUTPUT_TEX = TABLES_DIR / "table_12_heterogeneity_group_differences.tex"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export pairwise heterogeneity group-difference diagnostics.")
    parser.add_argument("--cate-with-groups-path", type=Path, default=DEFAULT_CATE_WITH_GROUPS_PATH)
    parser.add_argument("--cate-path", type=Path, default=DEFAULT_CATE_PATH)
    parser.add_argument("--model-input-path", type=Path, default=DEFAULT_MODEL_INPUT_PATH)
    parser.add_argument("--output-csv-path", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-tex-path", type=Path, default=DEFAULT_OUTPUT_TEX)
    parser.add_argument("--n-bootstrap", type=int, default=2000)
    parser.add_argument("--random-seed", type=int, default=RANDOM_SEED)
    return parser


def load_or_build_cate_with_groups(cate_with_groups_path: Path, cate_path: Path, model_input_path: Path) -> pd.DataFrame:
    if cate_with_groups_path.exists():
        return pd.read_csv(cate_with_groups_path)
    cate = pd.read_csv(cate_path)
    model_input = pd.read_csv(model_input_path)
    _, attached = build_heterogeneity_group_summary(cate, model_input)
    cate_with_groups_path.parent.mkdir(parents=True, exist_ok=True)
    attached.to_csv(cate_with_groups_path, index=False)
    return attached


def format_latex_table(table: pd.DataFrame) -> str:
    display = table[
        [
            "dimension_cn",
            "group_a_cn",
            "group_b_cn",
            "cate_mean_a",
            "cate_mean_b",
            "mean_difference_a_minus_b",
            "ci_lower_bootstrap",
            "ci_upper_bootstrap",
            "p_value_approx",
            "direction_cn",
        ]
    ].copy()
    display.columns = [
        "异质性维度",
        "组A",
        "组B",
        "组A CATE均值",
        "组B CATE均值",
        "组A-组B差异",
        "Bootstrap CI下限",
        "Bootstrap CI上限",
        "近似P值",
        "方向",
    ]
    numeric_columns = [
        "组A CATE均值",
        "组B CATE均值",
        "组A-组B差异",
        "Bootstrap CI下限",
        "Bootstrap CI上限",
        "近似P值",
    ]
    for column in numeric_columns:
        display[column] = display[column].map(lambda value: f"{float(value):.4f}")
    return display.to_latex(
        index=False,
        escape=False,
        caption="异质性分组CATE均值组间差异诊断（城市层面Bootstrap）",
        label="tab:heterogeneity_group_differences",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_project_directories()
    cate_with_groups = load_or_build_cate_with_groups(
        cate_with_groups_path=args.cate_with_groups_path,
        cate_path=args.cate_path,
        model_input_path=args.model_input_path,
    )
    table = build_pairwise_group_differences(
        cate_with_groups=cate_with_groups,
        n_bootstrap=args.n_bootstrap,
        random_seed=args.random_seed,
    )
    csv_path = write_table(table, args.output_csv_path)
    args.output_tex_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_tex_path.write_text(format_latex_table(table), encoding="utf-8")
    print(f"Heterogeneity group differences CSV written to: {csv_path}")
    print(f"Heterogeneity group differences LaTeX written to: {args.output_tex_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
