from pathlib import Path
from subprocess import run
import zipfile


def test_prepare_submission_package_allows_missing_and_excludes_raw_data(tmp_path):
    project_root = tmp_path / "project"
    (project_root / "src").mkdir(parents=True)
    (project_root / "tests").mkdir()
    (project_root / "docs" / "paper").mkdir(parents=True)
    (project_root / "outputs" / "tables").mkdir(parents=True)
    (project_root / "outputs" / "figures").mkdir(parents=True)
    (project_root / "data" / "raw").mkdir(parents=True)

    (project_root / "README.md").write_text("# demo\n", encoding="utf-8")
    (project_root / "environment.yml").write_text("name: demo\n", encoding="utf-8")
    (project_root / "src" / "demo.py").write_text("print('ok')\n", encoding="utf-8")
    (project_root / "src" / "demo.pyc").write_text("skip\n", encoding="utf-8")
    (project_root / "src" / "__pycache__").mkdir()
    (project_root / "src" / "__pycache__" / "demo.pyc").write_text("skip\n", encoding="utf-8")
    (project_root / "tests" / "test_demo.py").write_text("def test_demo():\n    assert True\n", encoding="utf-8")
    (project_root / "docs" / "paper" / "03_manuscript_v0_2.md").write_text("paper\n", encoding="utf-8")
    (project_root / "docs" / "paper" / "04_submission_manuscript_candidate.md").write_text("# 候选稿\n\n正文\n", encoding="utf-8")
    (project_root / "outputs" / "tables" / "table_01_descriptive_statistics.csv").write_text("a\n1\n", encoding="utf-8")
    (project_root / "outputs" / "figures" / "figure_manifest.csv").write_text(
        "figure_id,filename,caption_cn,caption_en,source,status,caveat\n"
        "Figure 1,figure_01_digital_finance_carbon_intensity_trends.pdf,趋势图,Trend,source.csv,first_pass,Descriptive only.\n",
        encoding="utf-8",
    )
    (project_root / "outputs" / "figures" / "figure_01_digital_finance_carbon_intensity_trends.pdf").write_text("fake pdf placeholder", encoding="utf-8")
    (project_root / "data" / "raw" / "licensed.csv").write_text("do not copy\n", encoding="utf-8")

    result = run(
        [
            "python3",
            "src/32_prepare_submission_package.py",
            "--project-root",
            str(project_root),
            "--output-dir",
            str(tmp_path / "dist"),
            "--package-name",
            "bundle",
            "--allow-missing",
            "--no-zip",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    package_dir = tmp_path / "dist" / "bundle"
    assert (package_dir / "MANIFEST.md").exists()
    assert (package_dir / "data" / "DATA_NOTICE.md").exists()
    assert (package_dir / "paper" / "04_submission_manuscript_candidate.docx").exists()
    assert (package_dir / "code" / "src" / "demo.py").exists()
    assert not (package_dir / "code" / "src" / "demo.pyc").exists()
    assert not (package_dir / "code" / "src" / "__pycache__").exists()
    assert not (package_dir / "data" / "raw" / "licensed.csv").exists()
    manifest = (package_dir / "MANIFEST.md").read_text(encoding="utf-8")
    with zipfile.ZipFile(package_dir / "paper" / "04_submission_manuscript_candidate.docx") as archive:
        document_xml = archive.read("word/document.xml").decode("utf-8")
    assert "缺失资产数" in manifest
    assert "Word 初稿：已生成" in manifest
    assert "政策文本 LLM 模块当前 `not_ready`" in manifest
    assert "附录：图件清单" in document_xml
    assert "Figure 1 趋势图" in document_xml
