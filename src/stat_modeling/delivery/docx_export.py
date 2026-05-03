"""Small dependency-free Markdown-to-DOCX exporter for submission drafts.

The project environment does not currently provide pandoc/libreoffice and we avoid
adding new dependencies at this stage. This module creates a conservative Word
``.docx`` package with headings, paragraphs, simple bullet paragraphs, and
Chinese/English font defaults using only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
import re
import zipfile


REQUIRED_DOCX_MEMBERS = frozenset(
    {
        "[Content_Types].xml",
        "_rels/.rels",
        "docProps/app.xml",
        "docProps/core.xml",
        "word/document.xml",
        "word/settings.xml",
        "word/styles.xml",
    }
)


@dataclass(frozen=True)
class MarkdownBlock:
    kind: str
    text: str
    level: int = 0


def clean_inline_markdown(text: str) -> str:
    """Remove lightweight Markdown markers while preserving readable text."""
    text = re.sub(r"<!--.*?-->", "", text)
    text = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r"\1（\2）", text)
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("`", "")
    # Remove emphasis asterisks that are not likely multiplication signs.
    text = re.sub(r"(?<!\w)\*(?!\s)(.*?)\*(?!\w)", r"\1", text)
    text = text.replace("\\(", "(").replace("\\)", ")")
    text = text.replace("\\[", "[").replace("\\]", "]")
    return re.sub(r"\s+", " ", text).strip()


def parse_markdown_blocks(markdown_text: str) -> list[MarkdownBlock]:
    """Parse a conservative subset of Markdown into ordered document blocks."""
    blocks: list[MarkdownBlock] = []
    paragraph_lines: list[str] = []
    in_html_comment = False
    in_fence = False

    def flush_paragraph() -> None:
        if paragraph_lines:
            text = clean_inline_markdown(" ".join(paragraph_lines))
            if text:
                blocks.append(MarkdownBlock("paragraph", text))
            paragraph_lines.clear()

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if in_html_comment:
            if "-->" in stripped:
                in_html_comment = False
            continue
        if stripped.startswith("<!--"):
            if "-->" not in stripped:
                in_html_comment = True
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            in_fence = not in_fence
            continue
        if in_fence:
            if stripped:
                blocks.append(MarkdownBlock("code", stripped))
            continue

        if not stripped:
            flush_paragraph()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            level = min(len(heading.group(1)), 3)
            text = clean_inline_markdown(heading.group(2))
            if text:
                blocks.append(MarkdownBlock("heading", text, level))
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            text = clean_inline_markdown(stripped.lstrip("> "))
            if text:
                blocks.append(MarkdownBlock("quote", text))
            continue

        bullet = re.match(r"^[-*+]\s+(.+)$", stripped)
        if bullet:
            flush_paragraph()
            text = clean_inline_markdown(bullet.group(1))
            if text:
                blocks.append(MarkdownBlock("bullet", text))
            continue

        paragraph_lines.append(stripped)

    flush_paragraph()
    return blocks


def _xml_text(text: str) -> str:
    # XML 1.0 disallows most C0 controls; keep tab/newline/carriage return out of runs too.
    cleaned = "".join(ch for ch in text if ch >= " " or ch in "\t")
    return escape(cleaned, quote=False)


def _run_xml(text: str, bold: bool = False, size_half_points: int = 24) -> str:
    bold_xml = "<w:b/>" if bold else ""
    return (
        "<w:r>"
        "<w:rPr>"
        '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/>'
        f"{bold_xml}<w:sz w:val=\"{size_half_points}\"/><w:szCs w:val=\"{size_half_points}\"/>"
        "</w:rPr>"
        f"<w:t>{_xml_text(text)}</w:t>"
        "</w:r>"
    )


def _paragraph_xml(block: MarkdownBlock) -> str:
    if block.kind == "heading":
        style = f"Heading{block.level}"
        size = {1: 32, 2: 28, 3: 24}.get(block.level, 24)
        return (
            "<w:p>"
            f'<w:pPr><w:pStyle w:val="{style}"/><w:spacing w:before="180" w:after="120"/></w:pPr>'
            f"{_run_xml(block.text, bold=True, size_half_points=size)}"
            "</w:p>"
        )
    if block.kind == "bullet":
        return (
            "<w:p>"
            '<w:pPr><w:pStyle w:val="ListParagraph"/><w:ind w:left="420" w:hanging="210"/></w:pPr>'
            f"{_run_xml('• ' + block.text)}"
            "</w:p>"
        )
    if block.kind == "quote":
        return (
            "<w:p>"
            '<w:pPr><w:pStyle w:val="Quote"/><w:ind w:left="360"/></w:pPr>'
            f"{_run_xml(block.text, size_half_points=22)}"
            "</w:p>"
        )
    if block.kind == "code":
        return (
            "<w:p>"
            '<w:pPr><w:pStyle w:val="Code"/></w:pPr>'
            f"{_run_xml(block.text, size_half_points=20)}"
            "</w:p>"
        )
    return (
        "<w:p>"
        '<w:pPr><w:spacing w:after="120"/><w:jc w:val="both"/></w:pPr>'
        f"{_run_xml(block.text)}"
        "</w:p>"
    )


def build_document_xml(blocks: list[MarkdownBlock]) -> str:
    body = "".join(_paragraph_xml(block) for block in blocks)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>
'''


def content_types_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
'''


def package_relationships_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
'''


def styles_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="240" w:after="120"/></w:pPr>
    <w:rPr><w:b/><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="200" w:after="100"/></w:pPr>
    <w:rPr><w:b/><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="160" w:after="80"/></w:pPr>
    <w:rPr><w:b/><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/></w:style>
  <w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:basedOn w:val="Normal"/><w:rPr><w:i/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/><w:basedOn w:val="Normal"/><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:eastAsia="等线"/><w:sz w:val="20"/></w:rPr></w:style>
</w:styles>
'''


def settings_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:zoom w:percent="100"/>
  <w:defaultTabStop w:val="420"/>
</w:settings>
'''


def core_xml(title: str) -> str:
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{_xml_text(title)}</dc:title>
  <dc:creator>Statistical-Modeling project</dc:creator>
  <cp:lastModifiedBy>Statistical-Modeling project</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>
</cp:coreProperties>
'''


def app_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Statistical-Modeling DOCX exporter</Application>
</Properties>
'''


def export_markdown_to_docx(
    markdown_path: Path,
    output_path: Path,
    title: str | None = None,
    append_tables: list[DocxTable] | None = None,
) -> Path:
    """Export a Markdown file to a simple Word ``.docx`` file."""
    markdown_text = markdown_path.read_text(encoding="utf-8")
    blocks = parse_markdown_blocks(markdown_text)
    if not blocks:
        raise ValueError(f"No exportable Markdown blocks found in {markdown_path}")
    inferred_title = title or next((block.text for block in blocks if block.kind == "heading"), markdown_path.stem)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml())
        archive.writestr("_rels/.rels", package_relationships_xml())
        archive.writestr("docProps/core.xml", core_xml(inferred_title))
        archive.writestr("docProps/app.xml", app_xml())
        archive.writestr("word/document.xml", build_document_xml_with_tables(blocks, append_tables))
        archive.writestr("word/styles.xml", styles_xml())
        archive.writestr("word/settings.xml", settings_xml())
    return output_path


def validate_docx_package(docx_path: Path) -> None:
    """Raise if the generated DOCX is missing required package members."""
    if not docx_path.exists() or docx_path.stat().st_size == 0:
        raise FileNotFoundError(f"DOCX does not exist or is empty: {docx_path}")
    with zipfile.ZipFile(docx_path) as archive:
        names = set(archive.namelist())
    missing = sorted(REQUIRED_DOCX_MEMBERS - names)
    if missing:
        raise ValueError(f"DOCX package missing required members: {missing}")

@dataclass(frozen=True)
class DocxTable:
    """A simple table appendix to render into the generated DOCX."""

    title: str
    rows: tuple[tuple[str, ...], ...]
    note: str = ""


def _table_cell_xml(text: str, bold: bool = False) -> str:
    shade = '<w:shd w:fill="D9EAF7"/>' if bold else ""
    return (
        "<w:tc>"
        f"<w:tcPr>{shade}<w:tcMar><w:top w:w=\"60\" w:type=\"dxa\"/><w:left w:w=\"60\" w:type=\"dxa\"/>"
        '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="60" w:type="dxa"/></w:tcMar></w:tcPr>'
        "<w:p><w:pPr><w:spacing w:after=\"0\"/></w:pPr>"
        f"{_run_xml(text, bold=bold, size_half_points=18)}"
        "</w:p>"
        "</w:tc>"
    )


def _table_xml(table: DocxTable) -> str:
    if not table.rows:
        return ""
    rows_xml: list[str] = []
    for row_index, row in enumerate(table.rows):
        cells = "".join(_table_cell_xml(cell, bold=row_index == 0) for cell in row)
        rows_xml.append(f"<w:tr>{cells}</w:tr>")
    borders = (
        '<w:tblBorders><w:top w:val="single" w:sz="6" w:space="0" w:color="808080"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>'
        '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="808080"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/></w:tblBorders>'
    )
    return (
        "<w:tbl>"
        f"<w:tblPr><w:tblW w:w=\"0\" w:type=\"auto\"/>{borders}"
        '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
        "</w:tblPr>"
        f"{''.join(rows_xml)}"
        "</w:tbl>"
    )


def _appendix_xml(tables: list[DocxTable]) -> str:
    if not tables:
        return ""
    parts = [_paragraph_xml(MarkdownBlock("heading", "附录：论文表格（供排版插入正文）", 1))]
    for table in tables:
        parts.append(_paragraph_xml(MarkdownBlock("heading", table.title, 2)))
        if table.note:
            parts.append(_paragraph_xml(MarkdownBlock("quote", table.note)))
        parts.append(_table_xml(table))
        parts.append(_paragraph_xml(MarkdownBlock("paragraph", " ")))
    return "".join(parts)


def build_document_xml_with_tables(blocks: list[MarkdownBlock], tables: list[DocxTable] | None = None) -> str:
    body = "".join(_paragraph_xml(block) for block in blocks)
    body += _appendix_xml(tables or [])
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>
'''
