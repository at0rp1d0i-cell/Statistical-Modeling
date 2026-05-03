import argparse
from pathlib import Path
from typing import Sequence

import pandas as pd

from stat_modeling.config import INTERIM_DATA_DIR
from stat_modeling.config import TABLES_DIR
from stat_modeling.config import ensure_project_directories
from stat_modeling.data.io import write_table


DEFAULT_DML_TABLE = TABLES_DIR / "table_02_dml_main_and_robustness.csv"
DEFAULT_TWFE_TABLE = TABLES_DIR / "table_06_ols_twfe_candidate.csv"
DEFAULT_PLACEBO_SUMMARY = TABLES_DIR / "table_07_dml_placebo_candidate_summary.csv"
DEFAULT_LEARNER_TABLE = TABLES_DIR / "table_08_dml_learner_replacement_candidate.csv"
DEFAULT_POPULATION_SENSITIVITY_TABLE = TABLES_DIR / "table_11_population_sensitivity_robustness.csv"
DEFAULT_CATE_SUMMARY = INTERIM_DATA_DIR / "modeling" / "heterogeneity_candidate_cate_summary.csv"
DEFAULT_HETEROGENEITY_GROUP_TABLE = TABLES_DIR / "table_10_heterogeneity_group_summary.csv"
DEFAULT_POLICY_TABLE = TABLES_DIR / "table_05_policy_seed_mechanism_candidate.csv"
DEFAULT_OUTPUT_CSV = TABLES_DIR / "table_09_current_evidence_synthesis.csv"
DEFAULT_OUTPUT_TEX = TABLES_DIR / "table_09_current_evidence_synthesis.tex"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export a current evidence-chain synthesis table for the manuscript.")
    parser.add_argument("--dml-table-path", type=Path, default=DEFAULT_DML_TABLE)
    parser.add_argument("--twfe-table-path", type=Path, default=DEFAULT_TWFE_TABLE)
    parser.add_argument("--placebo-summary-path", type=Path, default=DEFAULT_PLACEBO_SUMMARY)
    parser.add_argument("--learner-table-path", type=Path, default=DEFAULT_LEARNER_TABLE)
    parser.add_argument("--population-sensitivity-table-path", type=Path, default=DEFAULT_POPULATION_SENSITIVITY_TABLE)
    parser.add_argument("--cate-summary-path", type=Path, default=DEFAULT_CATE_SUMMARY)
    parser.add_argument("--heterogeneity-group-table-path", type=Path, default=DEFAULT_HETEROGENEITY_GROUP_TABLE)
    parser.add_argument("--policy-table-path", type=Path, default=DEFAULT_POLICY_TABLE)
    parser.add_argument("--output-csv-path", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-tex-path", type=Path, default=DEFAULT_OUTPUT_TEX)
    return parser


def require_columns(frame: pd.DataFrame, required: list[str], source: Path) -> None:
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"{source} missing required columns: {missing}")


def fmt(value: float, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}"


def find_row(frame: pd.DataFrame, column: str, value: str, source: Path) -> pd.Series:
    require_columns(frame, [column], source)
    subset = frame.loc[frame[column] == value]
    if subset.empty:
        raise ValueError(f"{source} has no row where {column} == {value}")
    return subset.iloc[0]


def build_evidence_synthesis(
    dml: pd.DataFrame,
    twfe: pd.DataFrame,
    placebo: pd.DataFrame,
    learner: pd.DataFrame,
    population_sensitivity: pd.DataFrame | None,
    cate: pd.DataFrame,
    heterogeneity_group: pd.DataFrame | None,
    policy: pd.DataFrame,
    source_paths: dict[str, Path],
) -> pd.DataFrame:
    require_columns(dml, ["outcome_column", "ate", "ci_lower", "ci_upper", "p_value"], source_paths["dml"])
    require_columns(twfe, ["outcome_column", "coefficient", "ci_lower", "ci_upper", "p_value"], source_paths["twfe"])
    require_columns(
        placebo,
        ["true_ate", "placebo_q025", "placebo_q975", "empirical_p_value", "permutations"],
        source_paths["placebo"],
    )
    require_columns(learner, ["learner_label", "ate", "p_value"], source_paths["learner"])
    if population_sensitivity is not None and not population_sensitivity.empty:
        require_columns(
            population_sensitivity,
            ["spec_key", "ate", "ci_lower", "ci_upper", "p_value", "ate_delta_vs_baseline"],
            source_paths["population_sensitivity"],
        )
    require_columns(cate, ["cate_mean", "cate_median"], source_paths["cate"])
    require_columns(policy, ["variable_name", "nobs"], source_paths["policy"])
    if heterogeneity_group is not None and not heterogeneity_group.empty:
        require_columns(
            heterogeneity_group,
            ["dimension_cn", "group_cn", "cate_mean", "n_city"],
            source_paths["heterogeneity_group"],
        )

    main_dml = find_row(dml, "outcome_column", "co2_emission_intensity", source_paths["dml"])
    total_dml = find_row(dml, "outcome_column", "co2_emission_total", source_paths["dml"])
    twfe_intensity = find_row(twfe, "outcome_column", "co2_emission_intensity", source_paths["twfe"])
    twfe_total = find_row(twfe, "outcome_column", "co2_emission_total", source_paths["twfe"])
    placebo_row = placebo.iloc[0]
    learner_ates = learner["ate"].astype(float)
    learner_p = learner["p_value"].astype(float)
    if population_sensitivity is not None and not population_sensitivity.empty:
        population_row = find_row(
            population_sensitivity,
            "spec_key",
            "population_augmented",
            source_paths["population_sensitivity"],
        )
        population_source = "Table 11"
        population_core = (
            f"加入人口ATE={fmt(population_row['ate'])}, "
            f"95%CI=[{fmt(population_row['ci_lower'])}, {fmt(population_row['ci_upper'])}], "
            f"p={fmt(population_row['p_value'])}, Δ={fmt(population_row['ate_delta_vs_baseline'])}"
        )
        population_direction = "负向但不显著" if float(population_row["p_value"]) >= 0.05 else "负向显著"
        population_support = "提示口径敏感" if float(population_row["p_value"]) >= 0.05 else "支持"
        population_boundary = "人口变量仅作敏感性控制；加入后效应收缩，主结论需保留口径敏感性说明。"
    else:
        population_source = "未读取"
        population_core = "人口敏感性表未生成"
        population_direction = "缺失"
        population_support = "待补"
        population_boundary = "需运行 src/28_export_population_sensitivity.py。"

    cate_row = cate.iloc[0]
    if heterogeneity_group is not None and not heterogeneity_group.empty:
        group_work = heterogeneity_group.copy()
        group_work["cate_mean"] = group_work["cate_mean"].astype(float)
        strongest_group = group_work.loc[group_work["cate_mean"].idxmin()]
        heterogeneity_source = "Table 10 / Figure 6"
        heterogeneity_core = (
            f"分组数={len(group_work)}, 最负组={strongest_group['dimension_cn']}-{strongest_group['group_cn']}, "
            f"CATE均值={fmt(strongest_group['cate_mean'])}"
        )
        heterogeneity_direction = "分组差异存在"
        heterogeneity_use = "正文异质性"
        heterogeneity_support = "提供异质性线索"
        heterogeneity_boundary = "基于当前CATE候选估计的分组摘要；近似区间不等同严格subgroup significance test。"
    else:
        heterogeneity_source = "Table 3 / Figure 3"
        heterogeneity_core = f"CATE均值={fmt(cate_row['cate_mean'])}, CATE中位数={fmt(cate_row['cate_median'])}"
        heterogeneity_direction = "总体负向"
        heterogeneity_use = "候选结果"
        heterogeneity_support = "方向一致"
        heterogeneity_boundary = "CATE技术预检查；正式分组表未读取。"

    rows = [
        {
            "序号": 1,
            "证据环节": "DML主结果",
            "来源": "Table 2 / Figure 2",
            "核心数值": f"ATE={fmt(main_dml['ate'])}, 95%CI=[{fmt(main_dml['ci_lower'])}, {fmt(main_dml['ci_upper'])}], p={fmt(main_dml['p_value'])}",
            "方向": "负向显著",
            "论文用途": "正文主结果",
            "对主命题支持": "支持",
            "边界说明": "当前2019—2023样本与方案B控制集。",
        },
        {
            "序号": 2,
            "证据环节": "替换结果变量",
            "来源": "Table 2 / Figure 2",
            "核心数值": f"总量ATE={fmt(total_dml['ate'], 2)}, 95%CI=[{fmt(total_dml['ci_lower'], 2)}, {fmt(total_dml['ci_upper'], 2)}], p={fmt(total_dml['p_value'])}",
            "方向": "负向显著",
            "论文用途": "正文稳健性",
            "对主命题支持": "支持",
            "边界说明": "碳排放总量与强度量纲不同。",
        },
        {
            "序号": 3,
            "证据环节": "OLS TWFE强度口径",
            "来源": "Table 6",
            "核心数值": f"系数={fmt(twfe_intensity['coefficient'])}, 95%CI=[{fmt(twfe_intensity['ci_lower'])}, {fmt(twfe_intensity['ci_upper'])}], p={fmt(twfe_intensity['p_value'])}",
            "方向": "负向显著",
            "论文用途": "正文稳健性",
            "对主命题支持": "支持",
            "边界说明": "传统线性基准参照，不替代DML。",
        },
        {
            "序号": 4,
            "证据环节": "OLS TWFE总量口径",
            "来源": "Table 6",
            "核心数值": f"系数={fmt(twfe_total['coefficient'])}, 95%CI=[{fmt(twfe_total['ci_lower'])}, {fmt(twfe_total['ci_upper'])}], p={fmt(twfe_total['p_value'])}",
            "方向": "未复制负向显著",
            "论文用途": "正文稳健性边界",
            "对主命题支持": "混合",
            "边界说明": "提示总量口径对线性TWFE较敏感。",
        },
        {
            "序号": 5,
            "证据环节": "DML安慰剂检验",
            "来源": "Table 7 / Figure 5",
            "核心数值": f"真实ATE={fmt(placebo_row['true_ate'])}, placebo 95%区间=[{fmt(placebo_row['placebo_q025'])}, {fmt(placebo_row['placebo_q975'])}], 经验p={fmt(placebo_row['empirical_p_value'])}",
            "方向": "真实值位于尾部",
            "论文用途": "正文稳健性",
            "对主命题支持": "支持",
            "边界说明": f"残差置换候选检验，置换次数={int(placebo_row['permutations'])}。",
        },
        {
            "序号": 6,
            "证据环节": "DML学习器替换",
            "来源": "Table 8",
            "核心数值": f"ATE范围=[{fmt(learner_ates.min())}, {fmt(learner_ates.max())}], 显著学习器={int((learner_p < 0.05).sum())}/{len(learner)}",
            "方向": "均为负向",
            "论文用途": "正文稳健性",
            "对主命题支持": "支持但强度敏感",
            "边界说明": "替换学习器后效应绝对值收缩，显著性接近5%。",
        },
        {
            "序号": 7,
            "证据环节": "人口变量敏感性",
            "来源": population_source,
            "核心数值": population_core,
            "方向": population_direction,
            "论文用途": "正文稳健性边界",
            "对主命题支持": population_support,
            "边界说明": population_boundary,
        },
        {
            "序号": 8,
            "证据环节": "正式异质性分组",
            "来源": heterogeneity_source,
            "核心数值": heterogeneity_core,
            "方向": heterogeneity_direction,
            "论文用途": heterogeneity_use,
            "对主命题支持": heterogeneity_support,
            "边界说明": heterogeneity_boundary,
        },
        {
            "序号": 9,
            "证据环节": "政策文本机制",
            "来源": "Table 5 / Figure 4",
            "核心数值": f"seed候选变量数={policy['variable_name'].nunique()}, 回归样本量={int(policy['nobs'].max())}",
            "方向": "技术链路跑通",
            "论文用途": "技术附录",
            "对主命题支持": "暂不作为正式机制证据",
            "边界说明": "seed rule-proxy，未完成完整语料与validated LLM scoring。",
        },
    ]
    return pd.DataFrame(rows)


def format_latex_table(table: pd.DataFrame) -> str:
    display = table[["证据环节", "来源", "核心数值", "对主命题支持", "边界说明"]].copy()
    return display.to_latex(
        index=False,
        escape=False,
        caption="当前结论证据链汇总（2019—2023 当前样本）",
        label="tab:current_evidence_synthesis",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_project_directories()
    source_paths = {
        "dml": args.dml_table_path,
        "twfe": args.twfe_table_path,
        "placebo": args.placebo_summary_path,
        "learner": args.learner_table_path,
        "population_sensitivity": args.population_sensitivity_table_path,
        "cate": args.cate_summary_path,
        "heterogeneity_group": args.heterogeneity_group_table_path,
        "policy": args.policy_table_path,
    }
    table = build_evidence_synthesis(
        dml=pd.read_csv(args.dml_table_path),
        twfe=pd.read_csv(args.twfe_table_path),
        placebo=pd.read_csv(args.placebo_summary_path),
        learner=pd.read_csv(args.learner_table_path),
        population_sensitivity=(
            pd.read_csv(args.population_sensitivity_table_path)
            if args.population_sensitivity_table_path.exists()
            else None
        ),
        cate=pd.read_csv(args.cate_summary_path),
        heterogeneity_group=pd.read_csv(args.heterogeneity_group_table_path) if args.heterogeneity_group_table_path.exists() else None,
        policy=pd.read_csv(args.policy_table_path),
        source_paths=source_paths,
    )
    csv_path = write_table(table, args.output_csv_path)
    args.output_tex_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_tex_path.write_text(format_latex_table(table), encoding="utf-8")
    print(f"Evidence synthesis CSV written to: {csv_path}")
    print(f"Evidence synthesis LaTeX written to: {args.output_tex_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
