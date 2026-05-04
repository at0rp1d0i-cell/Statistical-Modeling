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


DOCX_CORE_TABLE_SPECS = (
    SubmissionTableSpec("表1  描述性统计", "table_01_descriptive_statistics.csv"),
    SubmissionTableSpec("表2  DML 主结果与替换结果变量", "table_02_dml_main_and_robustness.csv"),
    SubmissionTableSpec("表7  DML 安慰剂检验摘要", "table_07_dml_placebo_candidate_summary.csv"),
    SubmissionTableSpec("表10  异质性分组摘要", "table_10_heterogeneity_group_summary.csv"),
    SubmissionTableSpec("表11  人口变量敏感性", "table_11_population_sensitivity_robustness.csv"),
    SubmissionTableSpec("表14  样本构造与覆盖情况", "table_14_sample_construction_coverage.csv", "数据可信度支撑表；不改变主规格。"),
)

# Default DOCX only attaches a compact set of core tables. The complete Table
# 1–15 CSV/TEX assets remain in outputs/tables and in the submission package for
# on-demand insertion during final Word/WPS editing.
DEFAULT_TABLE_SPECS = DOCX_CORE_TABLE_SPECS

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
    {
        "figure_id": "Figure 7",
        "filename": "figure_07_sample_coverage_by_year.pdf",
        "png_filename": "figure_07_sample_coverage_by_year.png",
        "jpg_filename": "figure_07_sample_coverage_by_year.jpg",
        "caption_cn": "DML 样本年度覆盖情况",
        "caption_en": "DML sample coverage by year",
        "source": "outputs/tables/table_14_sample_construction_coverage.csv",
        "status": "support_material",
        "caveat": "Sample construction support only; not causal evidence.",
    },
    {
        "figure_id": "Figure 8",
        "filename": "figure_08_robustness_evidence_forest.pdf",
        "png_filename": "figure_08_robustness_evidence_forest.png",
        "jpg_filename": "figure_08_robustness_evidence_forest.jpg",
        "caption_cn": "强度口径稳健性证据森林图",
        "caption_en": "Robustness evidence forest for intensity-scale estimates",
        "source": "outputs/tables/table_02/table_06/table_08/table_11",
        "status": "support_material",
        "caveat": "Synthesizes existing estimates; population sensitivity remains a boundary.",
    },
    {
        "figure_id": "Figure 9",
        "filename": "figure_09_regional_descriptive_trends.pdf",
        "png_filename": "figure_09_regional_descriptive_trends.png",
        "jpg_filename": "figure_09_regional_descriptive_trends.jpg",
        "caption_cn": "区域维度数字普惠金融与碳排放强度描述性趋势",
        "caption_en": "Regional descriptive trends in digital finance and carbon intensity",
        "source": "data/interim/modeling/dml_candidate_input_2019_2023.csv",
        "status": "support_material",
        "caveat": "Descriptive regional trend only; not causal evidence.",
    },
    {
        "figure_id": "Figure 10",
        "filename": "figure_10_research_framework.pdf",
        "png_filename": "figure_10_research_framework.png",
        "jpg_filename": "figure_10_research_framework.jpg",
        "caption_cn": "研究框架与技术路线图",
        "caption_en": "Research framework and technical route",
        "source": "docs/paper/04_submission_manuscript_candidate.md",
        "status": "support_material",
        "caveat": "Design-only route map; it summarizes the approved evidence chain and does not add a new empirical result.",
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
