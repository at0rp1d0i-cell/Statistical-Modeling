import argparse
from pathlib import Path
from typing import Sequence

import pandas as pd

from stat_modeling.config import INTERIM_DATA_DIR
from stat_modeling.config import TABLES_DIR
from stat_modeling.config import ensure_project_directories
from stat_modeling.data.io import read_table
from stat_modeling.data.io import write_table
from stat_modeling.data.io import write_text
from stat_modeling.policy_text.validation import build_llm_validation_readiness_table
from stat_modeling.policy_text.validation import validate_llm_score_records


DEFAULT_REGISTRY = INTERIM_DATA_DIR / "policy_text" / "policy_document_registry_seed_scored.csv"
DEFAULT_SCORE_TEMPLATE = INTERIM_DATA_DIR / "policy_text" / "policy_llm_score_review_template_seed.csv"
DEFAULT_DETAIL_OUTPUT = INTERIM_DATA_DIR / "policy_text" / "policy_llm_validation_detail_seed.csv"
DEFAULT_OUTPUT_CSV = TABLES_DIR / "table_13_policy_llm_validation_readiness.csv"
DEFAULT_OUTPUT_TEX = TABLES_DIR / "table_13_policy_llm_validation_readiness.tex"
DEFAULT_SUMMARY = INTERIM_DATA_DIR / "policy_llm_validation_readiness_summary.txt"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate policy LLM scoring readiness without fabricating scores.")
    parser.add_argument("--registry-path", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--score-path", type=Path, default=DEFAULT_SCORE_TEMPLATE)
    parser.add_argument("--detail-output-path", type=Path, default=DEFAULT_DETAIL_OUTPUT)
    parser.add_argument("--output-csv-path", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-tex-path", type=Path, default=DEFAULT_OUTPUT_TEX)
    parser.add_argument("--summary-path", type=Path, default=DEFAULT_SUMMARY)
    return parser


def format_latex_table(table: pd.DataFrame) -> str:
    display = table[
        [
            "total_registered_docs",
            "completed_score_rows",
            "range_valid_score_rows",
            "human_validated_rows",
            "validation_ready_rows",
            "readiness_status",
            "status_note",
        ]
    ].copy()
    display.columns = [
        "登记文档数",
        "已评分行数",
        "分数范围有效行数",
        "人工复核行数",
        "验证就绪行数",
        "状态",
        "说明",
    ]
    for column in ["登记文档数", "已评分行数", "分数范围有效行数", "人工复核行数", "验证就绪行数"]:
        display[column] = display[column].astype(int).astype(str)
    return display.to_latex(
        index=False,
        escape=False,
        caption="政策文本 LLM 评分验证就绪度（不含虚构分数）",
        label="tab:policy_llm_validation_readiness",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_project_directories()
    registry = read_table(args.registry_path)
    score_frame = read_table(args.score_path)
    detail = validate_llm_score_records(score_frame)
    write_table(detail, args.detail_output_path)
    readiness = build_llm_validation_readiness_table(score_frame, registry)
    write_table(readiness, args.output_csv_path)
    args.output_tex_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_tex_path.write_text(format_latex_table(readiness), encoding="utf-8")

    row = readiness.iloc[0]
    summary = "\n".join(
        [
            "Policy LLM Validation Readiness Summary",
            f"registry_path: {args.registry_path}",
            f"score_path: {args.score_path}",
            f"detail_output_path: {args.detail_output_path}",
            f"output_csv_path: {args.output_csv_path}",
            f"readiness_status: {row['readiness_status']}",
            f"validation_ready_rows: {int(row['validation_ready_rows'])}",
            f"total_registered_docs: {int(row['total_registered_docs'])}",
            "boundary_note: not_ready means policy text results remain technical scaffolding, not final LLM mechanism evidence.",
        ]
    ) + "\n"
    write_text(summary, args.summary_path)
    print(f"Policy LLM validation detail written to: {args.detail_output_path}")
    print(f"Policy LLM validation readiness CSV written to: {args.output_csv_path}")
    print(f"Policy LLM validation readiness LaTeX written to: {args.output_tex_path}")
    print(f"Summary written to: {args.summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
