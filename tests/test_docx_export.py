from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

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
