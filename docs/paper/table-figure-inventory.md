# 论文表图清单

本清单记录当前可复现表图资产、生成脚本和论文使用边界。`outputs/` 下生成物默认被 `.gitignore` 忽略；版本化合同以脚本、文稿和本清单为准。

## 文稿

| 编号 | 文件 | 当前状态 | 使用边界 |
| --- | --- | --- | --- |
| Manuscript v0.1 | `docs/paper/02_manuscript_v0_1.md` | 技术初稿完成，题目已确认数字普惠金融主线 | 可作为正文扩写底稿；最终定稿前需随人口稳健性、正式异质性和政策文本 validated LLM 结果更新 |
| Manuscript v0.2 | `docs/paper/03_manuscript_v0_2.md` | 可评审完整初稿完成 | 当前最完整正文底稿；可用于内部评审、答辩结构演练和后续格式化，正式提交前仍需补齐参考文献格式、表图排版和 AI 使用说明 |
| Submission candidate | `docs/paper/04_submission_manuscript_candidate.md` | 投稿候选稿完成 | 从 v0.2 整理而来，去除内部复现命令和表图清单，补入候选参考文献；用于转 Word、人工改写、查重和最终排版 |
| Submission DOCX | `dist/04_submission_manuscript_candidate.docx` | 本地生成 | 由 `src/33_export_submission_docx.py` 生成；默认将当前 Table 1–13 CSV 追加为文末表格附录，供 Word/WPS 编辑时移动到正文 |

## 表格

| 编号 | 文件 | 生成脚本 | 当前状态 | 论文使用边界 |
| --- | --- | --- | --- | --- |
| Table 1 | `outputs/tables/table_01_descriptive_statistics.csv` / `.tex` | `src/03_eda.py` | 首轮完成 | 当前 2019—2023 主分析样本描述统计；人口变量仅作为稳健性/敏感性候选展示，不进入主回归 |
| Table 2 | `outputs/tables/table_02_dml_main_and_robustness.csv` / `.tex` | `src/14_export_table_02.py` | 首轮完成 | 方案 B 主规格；不含 `population_control_candidate` |
| Table 3 | `outputs/tables/table_03_heterogeneity_candidate_summary.csv` / `.tex` | `src/15_export_table_03.py` | 候选完成 | CATE 技术结果摘要，作为正式分组异质性 Table 10 的前置基础 |
| Table 4 | `outputs/tables/table_04_heterogeneity_candidate_city_extremes.csv` / `.tex` | `src/16_export_table_04.py` | 候选完成 | 城市 CATE 极值展示，用于异质性附录或诊断，不作为 headline 分组结论 |
| Table 5 | `outputs/tables/table_05_policy_seed_mechanism_candidate.csv` / `.tex` | `src/23_mechanism_seed_regression.py`, `src/24_export_table_05.py` | seed 技术附录候选 | 只建议放在技术附录或机制模块说明中；不建议作为正文主结果表，不能写成最终 LLM 机制结论 |
| Table 6 | `outputs/tables/table_06_ols_twfe_candidate.csv` / `.tex` | `src/06_robustness.py` | 候选完成 | OLS 城市与年份双向固定效应对照；用于稳健性参照，不替代 DML 主识别 |
| Table 7 | `outputs/tables/table_07_dml_placebo_candidate_summary.csv` / `.tex` | `src/06_robustness.py` | 候选完成 | DML 残差置换安慰剂检验；若后续调整人口稳健性、样本补源或 DML 规格，需同步重跑 |
| Table 8 | `outputs/tables/table_08_dml_learner_replacement_candidate.csv` / `.tex` | `src/06_robustness.py` | 候选完成 | DML nuisance 学习器替换检验；当前方向稳定，最终规格锁定后需重跑 |
| Table 9 | `outputs/tables/table_09_current_evidence_synthesis.csv` / `.tex` | `src/26_export_evidence_synthesis.py` | 写作汇总完成 | 当前结论证据链汇总；不是新增模型结果，用于论文叙述和答辩沟通 |
| Table 10 | `outputs/tables/table_10_heterogeneity_group_summary.csv` / `.tex` | `src/27_export_heterogeneity_groups.py` | 首轮完成 | 区域、经济发展水平、产业结构三类正式异质性分组摘要；基于当前 CATE 候选估计，近似区间不等同于严格 subgroup significance test |
| Table 11 | `outputs/tables/table_11_population_sensitivity_robustness.csv` / `.tex` | `src/28_export_population_sensitivity.py` | 首轮完成 | 人口变量敏感性稳健性；人口不进入主规格，加入后 ATE 收缩且不显著，正文需作为口径敏感性边界说明 |
| Table 12 | `outputs/tables/table_12_heterogeneity_group_differences.csv` / `.tex` | `src/29_export_heterogeneity_group_differences.py` | 首轮完成 | 城市层面 CATE 均值 bootstrap 组间差异诊断；用于增强异质性叙述，不等同重新估计分组 DML |
| Table 13 | `outputs/tables/table_13_policy_llm_validation_readiness.csv` / `.tex` | `src/31_validate_policy_llm_scores.py` | 验证框架完成，当前 not_ready | 政策文本 LLM 评分验证就绪度；当前只记录评分准备与复核缺口，不作为正式机制证据 |

## 图形

| 编号 | 文件 | 生成脚本 | 当前状态 | 论文使用边界 |
| --- | --- | --- | --- | --- |
| Figure 1 | `outputs/figures/figure_01_digital_finance_carbon_intensity_trends.pdf` | `src/25_export_result_figures.py` | 首轮完成 | 描述性趋势，不是因果证据 |
| Figure 2 | `outputs/figures/figure_02_dml_effect_intervals.pdf` | `src/25_export_result_figures.py` | 首轮完成 | 展示当前 DML 主结果与总量稳健性估计区间 |
| Figure 3 | `outputs/figures/figure_03_candidate_cate_distribution.pdf` | `src/25_export_result_figures.py` | 候选完成 | CATE 分布预检查；正式解释维度已确认为区域、经济发展水平、产业结构 |
| Figure 4 | `outputs/figures/figure_04_policy_seed_mechanism_snapshot.pdf` | `src/25_export_result_figures.py` | seed 技术附录候选 | seed 中央政策规则代理覆盖与分数快照；不进入正文主结果，非 validated LLM scoring |
| Figure 5 | `outputs/figures/figure_05_dml_placebo_distribution.pdf` | `src/06_robustness.py` | 候选完成 | DML 残差置换安慰剂分布图；用于稳健性章节候选证据 |
| Figure 6 | `outputs/figures/figure_06_heterogeneity_groups.pdf` | `src/27_export_heterogeneity_groups.py` | 首轮完成 | 区域、经济发展水平、产业结构分组 CATE 均值与近似区间；用于异质性章节 |
| Figure manifest | `outputs/figures/figure_manifest.csv` | `src/25_export_result_figures.py` | 已生成 | 记录图形 caption、来源与 caveat |

## 2026-05-03 本地重跑记录

- 已按 `docs/paper/submission-checklist.md` 的表图脚本顺序重跑：
  `src/03_eda.py`、`src/06_robustness.py`、`src/28_export_population_sensitivity.py`、`src/27_export_heterogeneity_groups.py`、`src/29_export_heterogeneity_group_differences.py`、`src/30_prepare_policy_llm_scoring_batch.py`、`src/31_validate_policy_llm_scores.py`、`src/26_export_evidence_synthesis.py`、`src/25_export_result_figures.py`。
- 生成物检查：`outputs/tables/table_01` 至 `table_13` 的当前合同文件均存在；所有 `table_*.tex` 均包含 `booktabs` 三线表结构。
- 图件检查：`outputs/figures/figure_01` 至 `figure_06` 的当前合同 PDF 均存在，`file` 识别为 1 页 PDF；`figure_manifest.csv` 已生成。
- 注意：`outputs/` 默认被 `.gitignore` 忽略；若最终提交包需要包含表图成品，应单独打包或按最终提交策略 force-add。

## 下一批表图缺口

1. 实际 LLM 评分执行与抽样人工复核（需填充 `policy_llm_score_review_template_seed.csv` 或完整语料版本）。
2. 异质性理论解释与政策含义段落。
3. 若后续调整样本、变量或模型规格，需再次重跑全部表图并更新本清单。
