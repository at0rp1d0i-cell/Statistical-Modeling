from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stat_modeling.delivery.submission_docx import export_submission_docx
from stat_modeling.delivery.submission_docx import load_submission_figures
from stat_modeling.delivery.submission_docx import load_submission_tables


def test_submission_docx_loads_existing_tables_only(tmp_path):
    tables_dir = tmp_path / "tables"
    tables_dir.mkdir()
    (tables_dir / "table_01_descriptive_statistics.csv").write_text("变量,均值\nY,1.0\n", encoding="utf-8")

    tables = load_submission_tables(tables_dir)

    assert len(tables) == 1
    assert tables[0].title.startswith("Table 1")
    assert tables[0].rows[1] == ("Y", "1.0")


def test_export_submission_docx_includes_table_appendix(tmp_path):
    manuscript = tmp_path / "candidate.md"
    output = tmp_path / "candidate.docx"
    tables_dir = tmp_path / "tables"
    figures_dir = tmp_path / "figures"
    tables_dir.mkdir()
    figures_dir.mkdir()
    manuscript.write_text("# 投稿候选稿\n\n正文。\n", encoding="utf-8")
    (tables_dir / "table_01_descriptive_statistics.csv").write_text("变量,均值\nY,1.0\n", encoding="utf-8")
    (figures_dir / "figure_manifest.csv").write_text(
        "figure_id,filename,caption_cn,caption_en,source,status,caveat\n"
        "Figure 1,figure_01.pdf,趋势图,Trend,source.csv,first_pass,Descriptive only.\n",
        encoding="utf-8",
    )
    (figures_dir / "figure_01.pdf").write_text("fake pdf placeholder", encoding="utf-8")

    export_submission_docx(manuscript, output, tables_dir=tables_dir, figures_dir=figures_dir)

    with zipfile.ZipFile(output) as archive:
        document_xml = archive.read("word/document.xml").decode("utf-8")

    assert "投稿候选稿" in document_xml
    assert "附录：论文表格" in document_xml
    assert "附录：图件清单" in document_xml
    assert "Table 1 描述性统计" in document_xml
    assert "Figure 1 趋势图" in document_xml
    assert "Y" in document_xml


def test_submission_docx_uses_fallback_figures(tmp_path):
    figures_dir = tmp_path / "figures"
    figures_dir.mkdir()
    (figures_dir / "figure_05_dml_placebo_distribution.pdf").write_text("fake pdf placeholder", encoding="utf-8")

    figures = load_submission_figures(figures_dir)

    assert len(figures) == 1
    assert figures[0].figure_id == "Figure 5"
    assert figures[0].caption_cn == "DML 残差置换安慰剂检验分布"
