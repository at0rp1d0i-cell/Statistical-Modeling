# 论文表图清单

本清单记录当前可复现表图资产、生成脚本和论文使用边界。`outputs/` 下生成物默认被 `.gitignore` 忽略；版本化合同以脚本、文稿和本清单为准。

## 表格

| 编号 | 文件 | 生成脚本 | 当前状态 | 论文使用边界 |
| --- | --- | --- | --- | --- |
| Table 1 | 待生成 | 待补描述统计脚本 | 缺口 | 需要补变量描述统计、样本量、均值、标准差、最小最大值 |
| Table 2 | `outputs/tables/table_02_dml_main_and_robustness.csv` / `.tex` | `src/14_export_table_02.py` | 首轮完成 | 方案 B 主规格；不含 `population_control_candidate` |
| Table 3 | `outputs/tables/table_03_heterogeneity_candidate_summary.csv` / `.tex` | `src/15_export_table_03.py` | 候选完成 | CATE 技术结果摘要，非最终 headline 异质性结论 |
| Table 4 | `outputs/tables/table_04_heterogeneity_candidate_city_extremes.csv` / `.tex` | `src/16_export_table_04.py` | 候选完成 | 城市 CATE 极值展示，非最终 headline 异质性结论 |
| Table 5 | `outputs/tables/table_05_policy_seed_mechanism_candidate.csv` / `.tex` | `src/23_mechanism_seed_regression.py`, `src/24_export_table_05.py` | seed 候选完成 | 规则代理 seed 机制证据，不能写成最终 LLM 机制结论 |

## 图形

| 编号 | 文件 | 生成脚本 | 当前状态 | 论文使用边界 |
| --- | --- | --- | --- | --- |
| Figure 1 | `outputs/figures/figure_01_digital_finance_carbon_intensity_trends.pdf` | `src/25_export_result_figures.py` | 首轮完成 | 描述性趋势，不是因果证据 |
| Figure 2 | `outputs/figures/figure_02_dml_effect_intervals.pdf` | `src/25_export_result_figures.py` | 首轮完成 | 展示当前 DML 主结果与总量稳健性估计区间 |
| Figure 3 | `outputs/figures/figure_03_candidate_cate_distribution.pdf` | `src/25_export_result_figures.py` | 候选完成 | CATE 分布预检查，异质性解释变量仍待最终锁定 |
| Figure 4 | `outputs/figures/figure_04_policy_seed_mechanism_trends.pdf` | `src/25_export_result_figures.py` | seed 候选完成 | seed 中央政策规则代理趋势，非 validated LLM scoring |
| Figure manifest | `outputs/figures/figure_manifest.csv` | `src/25_export_result_figures.py` | 已生成 | 记录图形 caption、来源与 caveat |

## 下一批表图缺口

1. `Table 1` 描述统计表。
2. OLS 双向固定效应对照表。
3. 安慰剂检验分布图。
4. 正式异质性分组图（需先锁定 headline 分组）。
5. validated LLM 政策文本评分图/表（需先完成完整语料与校验）。
