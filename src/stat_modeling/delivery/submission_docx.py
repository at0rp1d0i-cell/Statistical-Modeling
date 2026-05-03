"""Submission DOCX assembly helpers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from stat_modeling.config import PROJECT_ROOT, TABLES_DIR
from stat_modeling.delivery.docx_export import DocxTable
from stat_modeling.delivery.docx_export import export_markdown_to_docx
from stat_modeling.delivery.docx_export import validate_docx_package


DEFAULT_INPUT = PROJECT_ROOT / "docs" / "paper" / "04_submission_manuscript_candidate.md"
DEFAULT_OUTPUT = PROJECT_ROOT / "dist" / "04_submission_manuscript_candidate.docx"


@dataclass(frozen=True)
class SubmissionTableSpec:
    title: str
    filename: str
    note: str = ""


DEFAULT_TABLE_SPECS = (
    SubmissionTableSpec("Table 1 描述性统计", "table_01_descriptive_statistics.csv"),
    SubmissionTableSpec("Table 2 DML 主结果与替换结果变量", "table_02_dml_main_and_robustness.csv"),
    SubmissionTableSpec("Table 3 CATE 技术摘要", "table_03_heterogeneity_candidate_summary.csv"),
    SubmissionTableSpec("Table 4 CATE 城市极值诊断", "table_04_heterogeneity_candidate_city_extremes.csv"),
    SubmissionTableSpec("Table 5 政策文本 seed 机制候选", "table_05_policy_seed_mechanism_candidate.csv", "技术附录候选；非最终 LLM 机制证据。"),
    SubmissionTableSpec("Table 6 OLS 双向固定效应对照", "table_06_ols_twfe_candidate.csv"),
    SubmissionTableSpec("Table 7 DML 安慰剂检验摘要", "table_07_dml_placebo_candidate_summary.csv"),
    SubmissionTableSpec("Table 8 DML 学习器替换检验", "table_08_dml_learner_replacement_candidate.csv"),
    SubmissionTableSpec("Table 9 当前证据链汇总", "table_09_current_evidence_synthesis.csv", "写作/答辩汇总表，不替代模型结果表。"),
    SubmissionTableSpec("Table 10 异质性分组摘要", "table_10_heterogeneity_group_summary.csv"),
    SubmissionTableSpec("Table 11 人口变量敏感性", "table_11_population_sensitivity_robustness.csv"),
    SubmissionTableSpec("Table 12 异质性组间差异诊断", "table_12_heterogeneity_group_differences.csv"),
    SubmissionTableSpec("Table 13 政策文本 LLM 验证就绪度", "table_13_policy_llm_validation_readiness.csv", "当前 not_ready；只能作为验证边界说明。"),
)


def read_csv_table(path: Path, title: str, note: str = "", max_cell_chars: int = 80) -> DocxTable:
    """Read a CSV file into a simple DOCX table model."""
    rows: list[tuple[str, ...]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.reader(handle):
            cleaned = []
            for cell in row:
                value = " ".join(str(cell).split())
                if len(value) > max_cell_chars:
                    value = value[: max_cell_chars - 1] + "…"
                cleaned.append(value)
            rows.append(tuple(cleaned))
    return DocxTable(title=title, rows=tuple(rows), note=note)


def load_submission_tables(
    tables_dir: Path = TABLES_DIR,
    specs: Iterable[SubmissionTableSpec] = DEFAULT_TABLE_SPECS,
) -> list[DocxTable]:
    """Load every existing paper table CSV as a DOCX appendix table."""
    tables: list[DocxTable] = []
    for spec in specs:
        path = tables_dir / spec.filename
        if path.exists():
            tables.append(read_csv_table(path, spec.title, note=spec.note))
    return tables


def export_submission_docx(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    tables_dir: Path = TABLES_DIR,
    include_table_appendix: bool = True,
) -> Path:
    """Export the submission candidate manuscript and optional table appendix to DOCX."""
    tables = load_submission_tables(tables_dir) if include_table_appendix else []
    export_markdown_to_docx(input_path, output_path, append_tables=tables)
    validate_docx_package(output_path)
    return output_path
