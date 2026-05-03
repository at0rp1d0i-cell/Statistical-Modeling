"""Prepare a reviewable competition submission bundle.

This script copies the manuscript draft, reference files, paper-facing tables/figures,
and reproducibility code into a clean local bundle under ``dist/``. It intentionally
excludes raw data by default because raw archives may be licensed or too large for
GitHub/competition upload without a separate human decision.
"""

from __future__ import annotations

import argparse
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

from stat_modeling.config import PROJECT_ROOT
from stat_modeling.delivery.submission_docx import export_submission_docx


PAPER_DOC_FILES = (
    "03_manuscript_v0_2.md",
    "04_submission_manuscript_candidate.md",
    "references.md",
    "references.bib",
    "submission-checklist.md",
    "table-figure-inventory.md",
    "decision-log.md",
)

TABLE_FILES = (
    "table_01_descriptive_statistics.csv",
    "table_01_descriptive_statistics.tex",
    "table_02_dml_main_and_robustness.csv",
    "table_02_dml_main_and_robustness.tex",
    "table_03_heterogeneity_candidate_summary.csv",
    "table_03_heterogeneity_candidate_summary.tex",
    "table_04_heterogeneity_candidate_city_extremes.csv",
    "table_04_heterogeneity_candidate_city_extremes.tex",
    "table_05_policy_seed_mechanism_candidate.csv",
    "table_05_policy_seed_mechanism_candidate.tex",
    "table_06_ols_twfe_candidate.csv",
    "table_06_ols_twfe_candidate.tex",
    "table_07_dml_placebo_candidate_summary.csv",
    "table_07_dml_placebo_candidate_summary.tex",
    "table_08_dml_learner_replacement_candidate.csv",
    "table_08_dml_learner_replacement_candidate.tex",
    "table_09_current_evidence_synthesis.csv",
    "table_09_current_evidence_synthesis.tex",
    "table_10_heterogeneity_group_summary.csv",
    "table_10_heterogeneity_group_summary.tex",
    "table_11_population_sensitivity_robustness.csv",
    "table_11_population_sensitivity_robustness.tex",
    "table_12_heterogeneity_group_differences.csv",
    "table_12_heterogeneity_group_differences.tex",
    "table_13_policy_llm_validation_readiness.csv",
    "table_13_policy_llm_validation_readiness.tex",
)

FIGURE_FILES = (
    "figure_01_digital_finance_carbon_intensity_trends.pdf",
    "figure_01_digital_finance_carbon_intensity_trends.png",
    "figure_01_digital_finance_carbon_intensity_trends.jpg",
    "figure_02_dml_effect_intervals.pdf",
    "figure_02_dml_effect_intervals.png",
    "figure_02_dml_effect_intervals.jpg",
    "figure_03_candidate_cate_distribution.pdf",
    "figure_03_candidate_cate_distribution.png",
    "figure_03_candidate_cate_distribution.jpg",
    "figure_04_policy_seed_mechanism_snapshot.pdf",
    "figure_04_policy_seed_mechanism_snapshot.png",
    "figure_04_policy_seed_mechanism_snapshot.jpg",
    "figure_05_dml_placebo_distribution.pdf",
    "figure_05_dml_placebo_distribution.png",
    "figure_05_dml_placebo_distribution.jpg",
    "figure_06_heterogeneity_groups.pdf",
    "figure_06_heterogeneity_groups.png",
    "figure_06_heterogeneity_groups.jpg",
    "figure_manifest.csv",
)

DERIVED_DATA_FILES = (
    "data/interim/modeling/modeling_candidate_panel_2019_2023.csv",
    "data/interim/modeling/pku_cmcc_candidate_panel_2019_2023.csv",
    "data/interim/modeling/heterogeneity_candidate_cate_with_groups.csv",
    "data/interim/policy_text/policy_document_registry_seed_central.csv",
    "data/interim/policy_text/policy_llm_scoring_batch_seed.jsonl",
    "data/interim/policy_text/policy_llm_score_review_template_seed.csv",
)

EXCLUDED_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git", ".omx"}
EXCLUDED_FILE_SUFFIXES = {".pyc", ".pyo"}
SUBMISSION_MARKDOWN_IN_PACKAGE = Path("paper/04_submission_manuscript_candidate.md")
SUBMISSION_DOCX_IN_PACKAGE = Path("paper/04_submission_manuscript_candidate.docx")


@dataclass(frozen=True)
class Asset:
    source: Path
    destination: Path
    required: bool = True
    is_tree: bool = False
    note: str = ""


@dataclass(frozen=True)
class PackageResult:
    package_dir: Path
    zip_path: Path | None
    copied: tuple[Asset, ...]
    missing: tuple[Asset, ...]


def build_asset_plan(project_root: Path, include_derived_data: bool = False) -> list[Asset]:
    """Return the files/directories expected in the local submission bundle."""
    assets: list[Asset] = [
        Asset(project_root / "README.md", Path("code/README.md")),
        Asset(project_root / "environment.yml", Path("code/environment.yml")),
        Asset(project_root / "src", Path("code/src"), is_tree=True),
        Asset(project_root / "tests", Path("code/tests"), is_tree=True),
    ]

    for filename in PAPER_DOC_FILES:
        assets.append(Asset(project_root / "docs" / "paper" / filename, Path("paper") / filename))
    for filename in TABLE_FILES:
        assets.append(Asset(project_root / "outputs" / "tables" / filename, Path("outputs/tables") / filename))
    for filename in FIGURE_FILES:
        assets.append(Asset(project_root / "outputs" / "figures" / filename, Path("outputs/figures") / filename))

    if include_derived_data:
        for relative in DERIVED_DATA_FILES:
            assets.append(
                Asset(
                    project_root / relative,
                    Path("data/derived") / Path(relative).name,
                    required=False,
                    note="Derived/interim data; raw licensed archives are still excluded.",
                )
            )

    return assets


def should_skip(path: Path) -> bool:
    return path.name in EXCLUDED_DIR_NAMES or path.suffix in EXCLUDED_FILE_SUFFIXES


def copy_tree_filtered(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)

    def ignore(directory: str, names: list[str]) -> set[str]:
        return {name for name in names if should_skip(Path(directory) / name)}

    shutil.copytree(source, destination, ignore=ignore)


def copy_asset(asset: Asset, package_dir: Path) -> bool:
    if not asset.source.exists():
        return False
    target = package_dir / asset.destination
    target.parent.mkdir(parents=True, exist_ok=True)
    if asset.is_tree:
        copy_tree_filtered(asset.source, target)
    else:
        shutil.copy2(asset.source, target)
    return True


def write_data_notice(package_dir: Path, include_derived_data: bool) -> Path:
    notice = package_dir / "data" / "DATA_NOTICE.md"
    notice.parent.mkdir(parents=True, exist_ok=True)
    derived_line = "已按参数包含部分 derived/interim CSV/JSONL。" if include_derived_data else "默认未包含 derived/interim 数据。"
    notice.write_text(
        "# 数据提交说明\n\n"
        "本打包脚本默认不复制 `data/raw/` 原始数据，因为原始数据可能包含授权限制、体积限制或需要人工确认的数据源引用。\n\n"
        f"{derived_line}\n\n"
        "正式提交前需要由参赛队确认：\n\n"
        "1. 哪些原始数据允许随作品提交；\n"
        "2. 哪些数据只能在论文和 README 中说明来源；\n"
        "3. 是否需要提供最小可复现的派生建模表；\n"
        "4. PKU 指数、CMCC 碳排放数据和控制变量来源是否已经按要求引用。\n",
        encoding="utf-8",
    )
    return notice


def write_package_manifest(
    package_dir: Path,
    copied: Sequence[Asset],
    missing: Sequence[Asset],
    include_derived_data: bool,
) -> Path:
    manifest = package_dir / "MANIFEST.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    docx_generated = (package_dir / SUBMISSION_DOCX_IN_PACKAGE).exists()
    lines = [
        "# 提交包清单",
        "",
        f"生成时间：{now}",
        "",
        "## 内容结构",
        "",
        "- `paper/`：论文 Markdown 初稿、带表格和图件清单附录的 Word 初稿、参考文献、提交清单和表图清单。",
        "- `outputs/tables/`：论文表格 CSV 与 LaTeX。",
        "- `outputs/figures/`：论文图件 PDF 与 figure manifest。",
        "- `code/`：复现代码、测试与环境说明。",
        "- `data/DATA_NOTICE.md`：数据提交边界说明。",
        "",
        "## 当前研究边界",
        "",
        "- 主线题目：数字普惠金融的碳减排效应。",
        "- 主结果变量：碳排放强度。",
        "- 当前样本：2019—2023 年、294 个城市、1456 个 city-year 观测。",
        "- 人口变量不进入主回归，只作为敏感性检验。",
        "- 政策文本 LLM 模块当前 `not_ready`，只能作为方法创新/技术附录，不能写成最终机制证据。",
        "- AI 辅助生成的文稿必须经参赛队人工审阅、改写和确认后才能作为正式论文提交。",
        "",
        "## 复制结果",
        "",
        f"- 已复制资产数：{len(copied)}",
        f"- 缺失资产数：{len(missing)}",
        f"- Word 初稿：{'已生成（含表格和图件清单附录）' if docx_generated else '未生成'}",
        f"- 包含派生数据：{'是' if include_derived_data else '否'}",
        "",
    ]
    if missing:
        lines.extend(["## 缺失资产", ""])
        for asset in missing:
            required = "required" if asset.required else "optional"
            lines.append(f"- `{asset.source}` -> `{asset.destination}` ({required})")
        lines.append("")
    lines.extend(
        [
            "## 下一步人工任务",
            "",
            "1. 以 `paper/04_submission_manuscript_candidate.docx` 为 Word 初稿并人工改写、移动表格和插入图件。",
            "2. 按学校/赛区模板填写 AI 工具使用情况表、承诺书和报名表。",
            "3. 做查重并控制在官方要求范围内。",
            "4. 核对参考文献元数据和数据源引用。",
            "5. 决定最终提交是否包含 raw/derived 数据，或仅提交代码与数据说明。",
            "",
        ]
    )
    manifest.write_text("\n".join(lines), encoding="utf-8")
    return manifest


def write_submission_docx(package_dir: Path) -> Path | None:
    """Generate a DOCX draft inside the package when the Markdown candidate exists."""
    markdown_path = package_dir / SUBMISSION_MARKDOWN_IN_PACKAGE
    if not markdown_path.exists():
        return None
    docx_path = package_dir / SUBMISSION_DOCX_IN_PACKAGE
    export_submission_docx(
        markdown_path,
        docx_path,
        tables_dir=package_dir / "outputs" / "tables",
        figures_dir=package_dir / "outputs" / "figures",
    )
    return docx_path


def zip_directory(package_dir: Path) -> Path:
    zip_path = package_dir.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(package_dir.parent))
    return zip_path


def prepare_submission_package(
    project_root: Path,
    output_dir: Path,
    package_name: str,
    include_derived_data: bool = False,
    allow_missing: bool = False,
    make_zip: bool = True,
) -> PackageResult:
    package_dir = output_dir / package_name
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)

    copied: list[Asset] = []
    missing: list[Asset] = []
    for asset in build_asset_plan(project_root, include_derived_data=include_derived_data):
        if copy_asset(asset, package_dir):
            copied.append(asset)
        else:
            missing.append(asset)

    write_data_notice(package_dir, include_derived_data=include_derived_data)
    write_submission_docx(package_dir)
    write_package_manifest(package_dir, copied, missing, include_derived_data=include_derived_data)

    missing_required = [asset for asset in missing if asset.required]
    if missing_required and not allow_missing:
        missing_list = "\n".join(f"- {asset.source}" for asset in missing_required)
        raise FileNotFoundError(
            "Required submission assets are missing. Run the table/figure pipeline first or pass --allow-missing.\n"
            f"{missing_list}"
        )

    zip_path = zip_directory(package_dir) if make_zip else None
    return PackageResult(package_dir, zip_path, tuple(copied), tuple(missing))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare a local competition submission bundle under dist/.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "dist")
    parser.add_argument("--package-name", default="submission_package_current")
    parser.add_argument("--include-derived-data", action="store_true")
    parser.add_argument("--allow-missing", action="store_true")
    parser.add_argument("--no-zip", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    result = prepare_submission_package(
        project_root=args.project_root.resolve(),
        output_dir=args.output_dir.resolve(),
        package_name=args.package_name,
        include_derived_data=args.include_derived_data,
        allow_missing=args.allow_missing,
        make_zip=not args.no_zip,
    )
    print(f"Submission package written to: {result.package_dir}")
    if result.zip_path is not None:
        print(f"Submission package zip written to: {result.zip_path}")
    print(f"Copied assets: {len(result.copied)}")
    print(f"Missing assets: {len(result.missing)}")
    if result.missing:
        print("Review MANIFEST.md for missing asset details.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
