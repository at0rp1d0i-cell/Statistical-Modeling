import argparse
from pathlib import Path
from typing import Sequence

from stat_modeling.config import INTERIM_DATA_DIR
from stat_modeling.config import ensure_project_directories
from stat_modeling.data.io import read_table
from stat_modeling.data.io import write_table
from stat_modeling.data.io import write_text
from stat_modeling.policy_text.llm_schema import build_jsonl_batch
from stat_modeling.policy_text.validation import build_llm_score_review_template


DEFAULT_REGISTRY = INTERIM_DATA_DIR / "policy_text" / "policy_document_registry_seed_scored.csv"
DEFAULT_BATCH_JSONL = INTERIM_DATA_DIR / "policy_text" / "policy_llm_scoring_batch_seed.jsonl"
DEFAULT_REVIEW_TEMPLATE = INTERIM_DATA_DIR / "policy_text" / "policy_llm_score_review_template_seed.csv"
DEFAULT_SUMMARY = INTERIM_DATA_DIR / "policy_llm_scoring_batch_summary.txt"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare policy-document LLM scoring payloads and review template.")
    parser.add_argument("--registry-path", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--batch-jsonl-path", type=Path, default=DEFAULT_BATCH_JSONL)
    parser.add_argument("--review-template-path", type=Path, default=DEFAULT_REVIEW_TEMPLATE)
    parser.add_argument("--summary-path", type=Path, default=DEFAULT_SUMMARY)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_project_directories()
    registry = read_table(args.registry_path)
    args.batch_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    args.batch_jsonl_path.write_text(build_jsonl_batch(registry.to_dict(orient="records")), encoding="utf-8")

    review_template = build_llm_score_review_template(registry)
    write_table(review_template, args.review_template_path)

    summary = "\n".join(
        [
            "Policy LLM Scoring Batch Summary",
            f"registry_path: {args.registry_path}",
            f"batch_jsonl_path: {args.batch_jsonl_path}",
            f"review_template_path: {args.review_template_path}",
            f"documents: {len(registry)}",
            "boundary_note: this prepares payloads and a human/LLM review template only; it does not fabricate LLM scores.",
        ]
    ) + "\n"
    write_text(summary, args.summary_path)
    print(f"Policy LLM scoring JSONL written to: {args.batch_jsonl_path}")
    print(f"Policy LLM review template written to: {args.review_template_path}")
    print(f"Summary written to: {args.summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
