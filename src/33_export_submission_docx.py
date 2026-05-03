import argparse
from pathlib import Path
from typing import Iterable

from stat_modeling.delivery.submission_docx import DEFAULT_INPUT
from stat_modeling.delivery.submission_docx import DEFAULT_OUTPUT
from stat_modeling.delivery.submission_docx import export_submission_docx
from stat_modeling.config import FIGURES_DIR, TABLES_DIR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export the submission manuscript candidate Markdown to DOCX.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--tables-dir", type=Path, default=TABLES_DIR)
    parser.add_argument("--figures-dir", type=Path, default=FIGURES_DIR)
    parser.add_argument("--no-table-appendix", action="store_true")
    parser.add_argument("--no-figure-appendix", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    output_path = export_submission_docx(
        input_path=args.input,
        output_path=args.output,
        tables_dir=args.tables_dir,
        figures_dir=args.figures_dir,
        include_table_appendix=not args.no_table_appendix,
        include_figure_appendix=not args.no_figure_appendix,
    )
    print(f"DOCX written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
