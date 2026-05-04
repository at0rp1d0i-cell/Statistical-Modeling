# 论文表图清单

本清单记录当前可复现表图资产、生成脚本和论文使用边界。`outputs/` 下生成物默认被 `.gitignore` 忽略；版本化合同以脚本、文稿和本清单为准。

## 文稿

| 编号 | 文件 | 当前状态 | 使用边界 |
| --- | --- | --- | --- |
| Manuscript v0.1 | `docs/paper/02_manuscript_v0_1.md` | 技术初稿完成，题目已确认数字普惠金融主线 | 可作为正文扩写底稿；最终定稿前需随人口稳健性、正式异质性和政策文本 validated LLM 结果更新 |
| Manuscript v0.2 | `docs/paper/03_manuscript_v0_2.md` | 可评审完整初稿完成 | 当前最完整正文底稿；可用于内部评审、答辩结构演练和后续格式化，正式提交前仍需补齐参考文献格式、表图排版和 AI 使用说明 |
| Submission candidate | `docs/paper/04_submission_manuscript_candidate.md` | 投稿候选稿完成 | 从 v0.2 整理而来，去除内部复现命令和表图清单，补入候选参考文献；用于转 Word、人工改写、查重和最终排版 |
| Submission DOCX | `dist/04_submission_manuscript_candidate.docx` | 本地生成 | 由 `src/33_export_submission_docx.py` 生成；默认将当前 Table 1–15 CSV 和 Figure 1–9 插图清单追加为文末附录，图件提供 PDF/PNG/JPG，供 Word/WPS 编辑时移动到正文 |
| Final editing guide | `docs/paper/final-editing-guide.md` | 终稿编辑指南完成 | 规定正文/附录表图放置、Word/WPS 编辑顺序、识别边界和提交前人工核对项；随提交包复制到 `paper/final-editing-guide.md` |
| Materials review | `docs/paper/05_materials_and_adversarial_review.md` | 反向评估与素材清单完成 | 从评委质疑视角记录当前证据链软肋、新增支撑表图和下一轮增强方向 |

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
| Table 14 | `outputs/tables/table_14_sample_construction_coverage.csv` / `.tex` | `src/34_export_paper_support_materials.py` | 支撑素材完成 | 样本构造与覆盖情况；增强数据可信度，不作为因果证据 |
| Table 15 | `outputs/tables/table_15_variable_correlation_matrix.csv` / `.tex` | `src/34_export_paper_support_materials.py` | 支撑素材完成 | 主要变量相关系数矩阵；用于描述性关系和共线性初筛，不作为因果证据 |

## 图形

| 编号 | 文件 | 生成脚本 | 当前状态 | 论文使用边界 |
| --- | --- | --- | --- | --- |
| Figure 1 | `outputs/figures/figure_01_digital_finance_carbon_intensity_trends.pdf` | `src/25_export_result_figures.py` | 首轮完成 | 描述性趋势，不是因果证据 |
| Figure 2 | `outputs/figures/figure_02_dml_effect_intervals.pdf` | `src/25_export_result_figures.py` | 首轮完成 | 展示当前 DML 主结果与总量稳健性估计区间 |
| Figure 3 | `outputs/figures/figure_03_candidate_cate_distribution.pdf` | `src/25_export_result_figures.py` | 候选完成 | CATE 分布预检查；正式解释维度已确认为区域、经济发展水平、产业结构 |
| Figure 4 | `outputs/figures/figure_04_policy_seed_mechanism_snapshot.pdf` | `src/25_export_result_figures.py` | seed 技术附录候选 | seed 中央政策规则代理覆盖与分数快照；不进入正文主结果，非 validated LLM scoring |
| Figure 5 | `outputs/figures/figure_05_dml_placebo_distribution.pdf` | `src/06_robustness.py` | 候选完成 | DML 残差置换安慰剂分布图；用于稳健性章节候选证据 |
| Figure 6 | `outputs/figures/figure_06_heterogeneity_groups.pdf` | `src/27_export_heterogeneity_groups.py` | 首轮完成 | 区域、经济发展水平、产业结构分组 CATE 均值与近似区间；用于异质性章节 |
| Figure 7 | `outputs/figures/figure_07_sample_coverage_by_year.pdf` | `src/34_export_paper_support_materials.py` | 支撑素材完成 | DML 样本逐年覆盖；用于数据章节增强样本可信度 |
| Figure 8 | `outputs/figures/figure_08_robustness_evidence_forest.pdf` | `src/34_export_paper_support_materials.py` | 支撑素材完成 | 强度口径稳健性证据森林图；用于稳健性章节快速展示方向与人口敏感性边界 |
| Figure 9 | `outputs/figures/figure_09_regional_descriptive_trends.pdf` | `src/34_export_paper_support_materials.py` | 支撑素材完成 | 区域描述性趋势；用于异质性背景，不作为因果证据 |
| Figure 10 | `outputs/figures/figure_10_research_framework.pdf` | `src/34_export_paper_support_materials.py` | 支撑素材完成 | 研究框架与技术路线图；建议放在引言末尾或方法章节开头，只概括既有证据链 |
| Figure manifest | `outputs/figures/figure_manifest.csv` | `src/25_export_result_figures.py` | 已生成 | 记录 Figure 1—4 caption、来源与 caveat；Figure 5—10 由 DOCX fallback 规则补入图件清单 |

> 图件格式说明：`src/25_export_result_figures.py`、`src/06_robustness.py`、`src/27_export_heterogeneity_groups.py` 和 `src/34_export_paper_support_materials.py` 当前均会为论文图件同时输出 `.pdf`、`.png` 和 `.jpg`。论文正式排版优先使用 PDF 或 PNG；JPG 主要用于兼容只接受位图的场景。

## 正文与附录放置建议

- 正文优先：Table 1、Table 2、Table 6、Table 7、Table 8、Table 10、Table 11、Table 12、Table 14；Figure 1、Figure 2、Figure 5、Figure 6、Figure 7、Figure 8、Figure 10。
- 技术附录优先：Table 3、Table 4、Table 5、Table 9、Table 13、Table 15；Figure 3、Figure 4、Figure 9。
- Word/WPS 插图优先级：PDF（矢量） > PNG（排版兼容） > JPG（最后兼容备选）。
- 详细移动顺序和不可过度宣称边界见 `docs/paper/final-editing-guide.md`。

## 2026-05-04 本地重跑记录

- 本轮针对论文支撑素材重跑 `src/34_export_paper_support_materials.py`，新增并验证 Figure 10；其余 Table 1–15 与 Figure 1–9 沿用前次完整重跑记录。
- 生成物检查：`outputs/tables/table_01` 至 `table_15` 的当前合同文件均存在；所有 `table_*.tex` 均包含 `booktabs` 三线表结构。
- 图件检查：`outputs/figures/figure_01` 至 `figure_10` 的当前合同 PDF/PNG/JPG 均存在；`figure_manifest.csv` 已生成并由 DOCX fallback 补入 Figure 5—10。
- 注意：`outputs/` 默认被 `.gitignore` 忽略；若最终提交包需要包含表图成品，应单独打包或按最终提交策略 force-add。

## 下一批表图缺口

1. 实际 LLM 评分执行与抽样人工复核（需填充 `policy_llm_score_review_template_seed.csv` 或完整语料版本）。
2. 若需继续增强证明力，可单独确认数字普惠金融分项替换处理变量、滞后处理变量或分组 DML 再估计。
3. 若后续调整样本、变量或模型规格，需再次重跑全部表图并更新本清单。
