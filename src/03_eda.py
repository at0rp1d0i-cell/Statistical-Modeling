import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import pandas as pd

from stat_modeling.config import INTERIM_DATA_DIR
from stat_modeling.config import TABLES_DIR
from stat_modeling.config import ensure_project_directories
from stat_modeling.data.io import read_table
from stat_modeling.data.io import write_table


DEFAULT_INPUT_PATH = INTERIM_DATA_DIR / "modeling" / "dml_candidate_input_2019_2023.csv"
DEFAULT_OUTPUT_CSV = TABLES_DIR / "table_01_descriptive_statistics.csv"
DEFAULT_OUTPUT_TEX = TABLES_DIR / "table_01_descriptive_statistics.tex"


@dataclass(frozen=True)
class DescriptiveVariable:
    column: str
    label_cn: str
    label_en: str
    role_cn: str


TABLE_01_VARIABLES = [
    DescriptiveVariable(
        column="co2_emission_intensity",
        label_cn="碳排放强度",
        label_en="Carbon emission intensity",
        role_cn="主结果变量",
    ),
    DescriptiveVariable(
        column="co2_emission_total",
        label_cn="碳排放总量",
        label_en="Total carbon emissions",
        role_cn="稳健性结果变量",
    ),
    DescriptiveVariable(
        column="digital_inclusive_finance_index",
        label_cn="数字普惠金融指数",
        label_en="Digital inclusive finance index",
        role_cn="处理变量",
    ),
    DescriptiveVariable(
        column="dfi_coverage_breadth",
        label_cn="覆盖广度",
        label_en="Coverage breadth",
        role_cn="数字金融分项",
    ),
    DescriptiveVariable(
        column="dfi_usage_depth",
        label_cn="使用深度",
        label_en="Usage depth",
        role_cn="数字金融分项",
    ),
    DescriptiveVariable(
        column="dfi_digitization_level",
        label_cn="数字化程度",
        label_en="Digitization level",
        role_cn="数字金融分项",
    ),
    DescriptiveVariable(
        column="gdp_total",
        label_cn="地区生产总值",
        label_en="GDP",
        role_cn="当前主规格控制变量",
    ),
    DescriptiveVariable(
        column="secondary_industry_share",
        label_cn="第二产业占比",
        label_en="Secondary industry share",
        role_cn="当前主规格控制变量",
    ),
    DescriptiveVariable(
        column="fiscal_expenditure",
        label_cn="财政支出",
        label_en="Fiscal expenditure",
        role_cn="当前主规格控制变量",
    ),
    DescriptiveVariable(
        column="population_control_candidate",
        label_cn="人口规模（候选控制）",
        label_en="Population size (candidate control)",
        role_cn="候选控制变量，未锁定",
    ),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export Table 1 descriptive statistics for the current DML candidate sample."
    )
    parser.add_argument("--input-path", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-csv-path", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-tex-path", type=Path, default=DEFAULT_OUTPUT_TEX)
    return parser


def require_columns(frame: pd.DataFrame, required_columns: list[str], source: Path) -> None:
    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{source} missing required columns: {missing}")


def summarize_variable(series: pd.Series) -> dict[str, float | int]:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    return {
        "样本量": int(numeric.count()),
        "均值": numeric.mean(),
        "标准差": numeric.std(),
        "最小值": numeric.min(),
        "25%分位": numeric.quantile(0.25),
        "中位数": numeric.quantile(0.5),
        "75%分位": numeric.quantile(0.75),
        "最大值": numeric.max(),
    }


def build_descriptive_table(frame: pd.DataFrame, source_path: Path = DEFAULT_INPUT_PATH) -> pd.DataFrame:
    required_columns = [variable.column for variable in TABLE_01_VARIABLES]
    require_columns(frame, required_columns, source_path)
    rows: list[dict[str, object]] = []
    for variable in TABLE_01_VARIABLES:
        summary = summarize_variable(frame[variable.column])
        rows.append(
            {
                "变量": variable.label_cn,
                "英文变量": variable.label_en,
                "来源列": variable.column,
                "角色": variable.role_cn,
                **summary,
            }
        )
    table = pd.DataFrame(rows)
    numeric_columns = ["均值", "标准差", "最小值", "25%分位", "中位数", "75%分位", "最大值"]
    table[numeric_columns] = table[numeric_columns].round(4)
    return table


def format_latex_table(table: pd.DataFrame) -> str:
    display = table[["变量", "角色", "样本量", "均值", "标准差", "最小值", "中位数", "最大值"]].copy()
    for column in ["均值", "标准差", "最小值", "中位数", "最大值"]:
        display[column] = display[column].map(lambda value: "" if pd.isna(value) else f"{value:.4f}")
    display["样本量"] = display["样本量"].astype(int).astype(str)
    return display.to_latex(
        index=False,
        escape=False,
        caption="描述性统计：当前候选 DML 样本（2019—2023）",
        label="tab:descriptive_statistics",
    )


def export_table_01(
    frame: pd.DataFrame,
    output_csv_path: Path,
    output_tex_path: Path,
    source_path: Path = DEFAULT_INPUT_PATH,
) -> dict[str, Path]:
    table = build_descriptive_table(frame, source_path)
    csv_path = write_table(table, output_csv_path)
    output_tex_path.parent.mkdir(parents=True, exist_ok=True)
    output_tex_path.write_text(format_latex_table(table), encoding="utf-8")
    return {"csv_path": csv_path, "tex_path": output_tex_path}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_project_directories()
    frame = read_table(args.input_path)
    outputs = export_table_01(frame, args.output_csv_path, args.output_tex_path, args.input_path)
    print(f"CSV table written to: {outputs['csv_path']}")
    print(f"LaTeX table written to: {outputs['tex_path']}")
    print(
        "Boundary note: Table 1 describes the current candidate DML sample; "
        "population_control_candidate remains an unresolved candidate control."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
