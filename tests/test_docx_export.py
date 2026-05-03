from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stat_modeling.delivery.docx_export import DocxFigure
from stat_modeling.delivery.docx_export import DocxTable
from stat_modeling.delivery.docx_export import export_markdown_to_docx
from stat_modeling.delivery.docx_export import parse_markdown_blocks
from stat_modeling.delivery.docx_export import validate_docx_package


def test_parse_markdown_blocks_skips_comments_and_keeps_headings():
    blocks = parse_markdown_blocks(
        "<!-- internal -->\n\n# 标题\n\n## 二级\n\n正文 **重点** and *journal*.\n\n- 要点\n> 注释\n"
    )
    assert [block.kind for block in blocks] == ["heading", "heading", "paragraph", "bullet", "quote"]
    assert blocks[0].text == "标题"
    assert blocks[2].text == "正文 重点 and journal."


def test_export_markdown_to_docx_creates_valid_package(tmp_path):
    markdown = tmp_path / "paper.md"
    output = tmp_path / "paper.docx"
    markdown.write_text(
        "<!-- not exported -->\n\n# 主标题\n\n## 摘要\n\n正文包含 <xml> & 符号。\n\n- 第一条\n",
        encoding="utf-8",
    )

    export_markdown_to_docx(markdown, output)
    validate_docx_package(output)

    with zipfile.ZipFile(output) as archive:
        document_xml = archive.read("word/document.xml").decode("utf-8")
        names = set(archive.namelist())

    assert "[Content_Types].xml" in names
    assert "主标题" in document_xml
    assert "Heading1" in document_xml
    assert "• 第一条" in document_xml
    assert "not exported" not in document_xml
    assert "&lt;xml&gt; &amp; 符号" in document_xml


def test_export_markdown_to_docx_can_append_tables(tmp_path):
    markdown = tmp_path / "paper.md"
    output = tmp_path / "paper.docx"
    markdown.write_text("# 主标题\n\n正文。\n", encoding="utf-8")
    table = DocxTable(
        title="Table 1 测试表",
        rows=(("变量", "均值"), ("Y", "1.23")),
        note="供排版插入正文。",
    )

    export_markdown_to_docx(markdown, output, append_tables=[table])
    validate_docx_package(output)

    with zipfile.ZipFile(output) as archive:
        document_xml = archive.read("word/document.xml").decode("utf-8")

    assert "附录：论文表格" in document_xml
    assert "Table 1 测试表" in document_xml
    assert "变量" in document_xml
    assert "1.23" in document_xml
    assert "<w:tbl>" in document_xml


def test_export_markdown_to_docx_can_append_figure_list(tmp_path):
    markdown = tmp_path / "paper.md"
    output = tmp_path / "paper.docx"
    markdown.write_text("# 主标题\n\n正文。\n", encoding="utf-8")
    figure = DocxFigure(
        figure_id="Figure 1",
        filename="figure_01.pdf",
        png_filename="figure_01.png",
        jpg_filename="figure_01.jpg",
        caption_cn="趋势图",
        caption_en="Trend figure",
        caveat="Descriptive only.",
        source="outputs/tables/table_01.csv",
    )

    export_markdown_to_docx(markdown, output, append_figures=[figure])
    validate_docx_package(output)

    with zipfile.ZipFile(output) as archive:
        document_xml = archive.read("word/document.xml").decode("utf-8")

    assert "附录：图件清单" in document_xml
    assert "Figure 1 趋势图" in document_xml
    assert "outputs/figures/figure_01.pdf" in document_xml
    assert "outputs/figures/figure_01.png" in document_xml
    assert "outputs/figures/figure_01.jpg" in document_xml
    assert "Descriptive only." in document_xml
