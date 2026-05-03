import argparse
from pathlib import Path
from typing import Iterable

from stat_modeling.config import PROJECT_ROOT
from stat_modeling.delivery.docx_export import export_markdown_to_docx
from stat_modeling.delivery.docx_export import validate_docx_package


DEFAULT_INPUT = PROJECT_ROOT / "docs" / "paper" / "04_submission_manuscript_candidate.md"
DEFAULT_OUTPUT = PROJECT_ROOT / "dist" / "04_submission_manuscript_candidate.docx"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export the submission manuscript candidate Markdown to DOCX.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--title", default=None)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    output_path = export_markdown_to_docx(args.input, args.output, title=args.title)
    validate_docx_package(output_path)
    print(f"DOCX written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
