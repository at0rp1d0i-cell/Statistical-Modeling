"""Submission DOCX assembly helpers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from stat_modeling.config import FIGURES_DIR, PROJECT_ROOT, TABLES_DIR
from stat_modeling.delivery.docx_export import DocxFigure
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

FALLBACK_FIGURE_SPECS = (
    {
        "figure_id": "Figure 5",
        "filename": "figure_05_dml_placebo_distribution.pdf",
        "png_filename": "figure_05_dml_placebo_distribution.png",
        "jpg_filename": "figure_05_dml_placebo_distribution.jpg",
        "caption_cn": "DML 残差置换安慰剂检验分布",
        "caption_en": "DML residual-permutation placebo distribution",
        "source": "outputs/tables/table_07_dml_placebo_candidate_distribution.csv",
        "status": "candidate",
        "caveat": "Candidate robustness evidence; rerun if sample/specification changes.",
    },
    {
        "figure_id": "Figure 6",
        "filename": "figure_06_heterogeneity_groups.pdf",
        "png_filename": "figure_06_heterogeneity_groups.png",
        "jpg_filename": "figure_06_heterogeneity_groups.jpg",
        "caption_cn": "区域、经济发展水平和产业结构分组 CATE 均值",
        "caption_en": "Grouped CATE means by region, economic development, and industrial structure",
        "source": "outputs/tables/table_10_heterogeneity_group_summary.csv",
        "status": "first_pass",
        "caveat": "Grouped CATE summary and approximate intervals; not a subgroup DML re-estimation.",
    },
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


def read_figure_manifest(figures_dir: Path = FIGURES_DIR) -> list[dict[str, str]]:
    """Read figure manifest rows when available."""
    manifest = figures_dir / "figure_manifest.csv"
    if not manifest.exists():
        return []
    with manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def load_submission_figures(figures_dir: Path = FIGURES_DIR) -> list[DocxFigure]:
    """Load figure insertion records from the manifest plus known out-of-manifest figures."""
    rows = read_figure_manifest(figures_dir)
    by_id = {row.get("figure_id", ""): row for row in rows if row.get("figure_id")}
    for fallback in FALLBACK_FIGURE_SPECS:
        figure_path = figures_dir / fallback["filename"]
        if figure_path.exists() and fallback["figure_id"] not in by_id:
            by_id[fallback["figure_id"]] = fallback

    figures: list[DocxFigure] = []
    for figure_id in sorted(by_id, key=lambda value: int(value.split()[-1]) if value.split()[-1].isdigit() else 999):
        row = by_id[figure_id]
        filename = row.get("filename", "")
        if not filename or not (figures_dir / filename).exists():
            continue
        stem = Path(filename).stem
        png_filename = row.get("png_filename", "") or f"{stem}.png"
        jpg_filename = row.get("jpg_filename", "") or f"{stem}.jpg"
        if png_filename and not (figures_dir / png_filename).exists():
            png_filename = ""
        if jpg_filename and not (figures_dir / jpg_filename).exists():
            jpg_filename = ""
        figures.append(
            DocxFigure(
                figure_id=figure_id,
                filename=filename,
                png_filename=png_filename,
                jpg_filename=jpg_filename,
                caption_cn=row.get("caption_cn", ""),
                caption_en=row.get("caption_en", ""),
                caveat=row.get("caveat", ""),
                source=row.get("source", ""),
            )
        )
    return figures


def export_submission_docx(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    tables_dir: Path = TABLES_DIR,
    figures_dir: Path = FIGURES_DIR,
    include_table_appendix: bool = True,
    include_figure_appendix: bool = True,
) -> Path:
    """Export the submission candidate manuscript and optional table appendix to DOCX."""
    tables = load_submission_tables(tables_dir) if include_table_appendix else []
    figures = load_submission_figures(figures_dir) if include_figure_appendix else []
    export_markdown_to_docx(input_path, output_path, append_tables=tables, append_figures=figures)
    validate_docx_package(output_path)
    return output_path
