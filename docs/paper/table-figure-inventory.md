# 论文表图清单

本清单记录当前可复现表图资产、生成脚本和论文使用边界。`outputs/` 下生成物默认被 `.gitignore` 忽略；版本化合同以脚本、文稿和本清单为准。

## 文稿

| 编号 | 文件 | 当前状态 | 使用边界 |
| --- | --- | --- | --- |
| Manuscript v0.1 | `docs/paper/02_manuscript_v0_1.md` | 技术初稿完成 | 可作为正文扩写底稿；最终定稿前需随样本、规格、稳健性、异质性和政策文本结果更新 |

## 表格

| 编号 | 文件 | 生成脚本 | 当前状态 | 论文使用边界 |
| --- | --- | --- | --- | --- |
| Table 1 | `outputs/tables/table_01_descriptive_statistics.csv` / `.tex` | `src/03_eda.py` | 首轮完成 | 当前 2019—2023 候选 DML 样本描述统计；人口变量仍标记为候选控制，不能视为最终控制口径 |
| Table 2 | `outputs/tables/table_02_dml_main_and_robustness.csv` / `.tex` | `src/14_export_table_02.py` | 首轮完成 | 方案 B 主规格；不含 `population_control_candidate` |
| Table 3 | `outputs/tables/table_03_heterogeneity_candidate_summary.csv` / `.tex` | `src/15_export_table_03.py` | 候选完成 | CATE 技术结果摘要，非最终 headline 异质性结论 |
| Table 4 | `outputs/tables/table_04_heterogeneity_candidate_city_extremes.csv` / `.tex` | `src/16_export_table_04.py` | 候选完成 | 城市 CATE 极值展示，非最终 headline 异质性结论 |
| Table 5 | `outputs/tables/table_05_policy_seed_mechanism_candidate.csv` / `.tex` | `src/23_mechanism_seed_regression.py`, `src/24_export_table_05.py` | seed 技术附录候选 | 只建议放在技术附录或机制模块说明中；不建议作为正文主结果表，不能写成最终 LLM 机制结论 |
| Table 6 | `outputs/tables/table_06_ols_twfe_candidate.csv` / `.tex` | `src/06_robustness.py` | 候选完成 | OLS 城市与年份双向固定效应对照；用于稳健性参照，不替代 DML 主识别 |

## 图形

| 编号 | 文件 | 生成脚本 | 当前状态 | 论文使用边界 |
| --- | --- | --- | --- | --- |
| Figure 1 | `outputs/figures/figure_01_digital_finance_carbon_intensity_trends.pdf` | `src/25_export_result_figures.py` | 首轮完成 | 描述性趋势，不是因果证据 |
| Figure 2 | `outputs/figures/figure_02_dml_effect_intervals.pdf` | `src/25_export_result_figures.py` | 首轮完成 | 展示当前 DML 主结果与总量稳健性估计区间 |
| Figure 3 | `outputs/figures/figure_03_candidate_cate_distribution.pdf` | `src/25_export_result_figures.py` | 候选完成 | CATE 分布预检查，异质性解释变量仍待最终锁定 |
| Figure 4 | `outputs/figures/figure_04_policy_seed_mechanism_snapshot.pdf` | `src/25_export_result_figures.py` | seed 技术附录候选 | seed 中央政策规则代理覆盖与分数快照；不进入正文主结果，非 validated LLM scoring |
| Figure manifest | `outputs/figures/figure_manifest.csv` | `src/25_export_result_figures.py` | 已生成 | 记录图形 caption、来源与 caveat |

## 下一批表图缺口

1. 安慰剂检验分布图。
2. 学习器替换稳健性表。
3. 正式异质性分组图（需先锁定 headline 分组）。
4. validated LLM 政策文本评分图/表（需先完成完整语料与校验）。
5. 最终定稿前随最终样本与规格重跑 Table 1 和 Table 6。
