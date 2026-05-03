# 最终 Word 编辑指南

> 适用对象：从 `docs/paper/04_submission_manuscript_candidate.md` / `dist/04_submission_manuscript_candidate.docx` 进入正式 Word/WPS 排版的人工编辑阶段。本文档不改变研究设计，只规定终稿收口顺序、表图放置和不可过度宣称的边界。

## 1. 当前定稿基线

- 题目：`“双碳”战略下数字普惠金融的碳减排效应：基于中国地级市面板的双重机器学习因果推断与政策文本机制分析`。
- 主处理变量：`digital_inclusive_finance_index`，北京大学数字普惠金融指数。
- 主结果变量：`co2_emission_intensity`，碳排放强度。
- 主分析样本：2019—2023 年，294 个城市，1456 个 city-year 观测。
- 主模型：部分线性 DML，城市分组交叉拟合，城市聚类标准误。
- 政策文本模块：方法创新 / 技术附录；当前 LLM 验证状态为 `not_ready`。

## 2. Word/WPS 编辑顺序

1. 打开 `dist/04_submission_manuscript_candidate.docx` 或提交包内 `paper/04_submission_manuscript_candidate.docx`。
2. 另开 `docs/paper/04_submission_manuscript_candidate.md` 对照 Markdown 原文，避免 Word 自动格式化造成段落遗漏。
3. 先统一标题、摘要、关键词、一级/二级标题、脚注和参考文献格式。
4. 将文末表格附录中的核心表格移动到正文相应位置；移动后删除文末重复表格。
5. 从 `outputs/figures/` 插入图件：优先使用 PDF；若 Word/WPS 对 PDF 支持不好，使用 PNG；JPG 仅作为兼容备选。
6. 根据学校/赛区模板补齐 AI 工具使用情况表、承诺书、报名表。
7. 统计正文字符数（官方要求正文字符数计空格 ≤16000），压缩重复解释和技术细节。
8. 做查重与人工改写，保证最终提交稿不是 AI 原始输出。
9. 最后核对表图编号、交叉引用、参考文献、数据来源和附录说明。

## 3. 建议放入正文的表格

| 表号 | 建议位置 | 用途 | 编辑提醒 |
| --- | --- | --- | --- |
| Table 1 | 数据与变量章节 | 主分析样本描述统计 | 人口变量只能作为敏感性候选解释，不写入主回归变量集合。 |
| Table 2 | 基准结果章节 | DML 主结果与总量稳健性 | Headline 结论使用强度口径 ATE = -0.0540。 |
| Table 6 | 稳健性章节 | OLS 双向固定效应对照 | 写作上称为对照/稳健性，不替代 DML。 |
| Table 7 | 稳健性章节 | 残差置换安慰剂检验 | 和 Figure 5 配套展示真实 ATE 位于置换分布尾部。 |
| Table 8 | 稳健性章节 | 学习器替换检验 | 强调方向稳定，但效应大小存在模型敏感性。 |
| Table 10 | 异质性章节 | 区域、经济发展、产业结构分组摘要 | 表述为异质性线索/分组诊断。 |
| Table 11 | 稳健性或局限性章节 | 人口变量敏感性检验 | 必须披露加入人口后不显著，不能只写主规格显著。 |
| Table 12 | 异质性章节或附录 | 组间差异 bootstrap 诊断 | 不等同重新估计分组 DML。 |
| Table 14 | 数据章节或附录 | 样本构造与覆盖情况 | 用于解释 1456 个 city-year 来源，不作为因果证据。 |

## 4. 建议放入技术附录的表格

| 表号 | 建议位置 | 原因 |
| --- | --- | --- |
| Table 3 | 技术附录 | CATE 候选摘要，服务正式异质性解释。 |
| Table 4 | 技术附录 | 城市 CATE 极值诊断，避免正文过度展示个别城市。 |
| Table 5 | 技术附录 | policy seed 规则代理候选结果，不是 validated LLM 机制证据。 |
| Table 9 | 答辩材料或附录 | 证据链汇总，不是新增模型结果表。 |
| Table 13 | 技术附录 | LLM 验证就绪度为 `not_ready`，用于透明披露。 |
| Table 15 | 技术附录 | 相关系数矩阵用于描述性关系和共线性初筛，不作为因果证据。 |

## 5. 图件放置建议

| 图号 | 建议位置 | 文件 | 编辑提醒 |
| --- | --- | --- | --- |
| Figure 1 | 数据描述章节 | `figure_01_digital_finance_carbon_intensity_trends` | 描述趋势，不作为因果证据。 |
| Figure 2 | 基准结果章节 | `figure_02_dml_effect_intervals` | 与 Table 2 配套，展示估计区间。 |
| Figure 5 | 稳健性章节 | `figure_05_dml_placebo_distribution` | 与 Table 7 配套。 |
| Figure 6 | 异质性章节 | `figure_06_heterogeneity_groups` | 与 Table 10/12 配套。 |
| Figure 7 | 数据章节 | `figure_07_sample_coverage_by_year` | 展示样本覆盖，不作为因果证据。 |
| Figure 8 | 稳健性章节 | `figure_08_robustness_evidence_forest` | 汇总强度口径估计，并保留人口敏感性边界。 |
| Figure 3 | 技术附录 | `figure_03_candidate_cate_distribution` | CATE 分布诊断。 |
| Figure 4 | 技术附录 | `figure_04_policy_seed_mechanism_snapshot` | seed 规则代理快照，非正式 LLM 结果。 |
| Figure 9 | 技术附录或异质性背景 | `figure_09_regional_descriptive_trends` | 区域描述性趋势，不替代异质性模型结果。 |

> 文件格式：每张图均有 `.pdf`、`.png`、`.jpg` 三种版本。正式排版优先 PDF 或 PNG；若比赛平台只接受位图，使用 PNG。

## 6. 不要删除的识别边界

终稿中必须保留以下边界，避免结论过强：

1. **DML 边界**：DML 降低函数形式错设风险，但不能自动解决遗漏变量、反向因果或不可观测政策冲击。
2. **样本边界**：当前是 2019—2023 年主分析样本，不是完整长期平衡面板。
3. **人口敏感性边界**：加入人口变量后 ATE 收缩且不显著；这说明结论对控制变量口径敏感。
4. **异质性边界**：Table 10/12 是 CATE 分组诊断和 bootstrap 组间差异，不等同严格分组再估计或机制识别。
5. **政策文本边界**：Table 13 为 `not_ready`；未完成真实 LLM scoring 与人工复核前，不可写成正式机制实证结果。
6. **Table 9 边界**：Table 9 是证据链汇总/答辩辅助，不是回归结果。

## 7. 可使用的核心结论表述

- 稳妥表述：在当前控制变量和样本条件下，数字普惠金融提升与城市碳排放强度下降显著相关，DML 主规格给出负向平均处理效应证据。
- 稳健性表述：替换结果变量、OLS 双向固定效应对照、残差置换安慰剂检验和学习器替换总体支持主效应方向，但人口变量敏感性提示结论需保留口径边界。
- 异质性表述：减排效应在低经济发展水平城市以及西部、东北等区域更强，说明数字普惠金融的绿色效应具有发展阶段和区域条件依赖性。
- 政策文本表述：本文建立了政策文本机制分析的可复现链路，但当前 validated LLM 评分尚未完成，因此将其定位为方法创新和后续扩展方向。

## 8. 提交前人工核对清单

- [ ] 正文题目与“数字普惠金融”主线一致。
- [ ] 摘要中的数值与 Table 2、Table 7、Table 11 一致。
- [ ] 正文 Table/Figure 编号连续，无文末重复表格。
- [ ] Figure 2、Figure 5、Figure 6 插入后清晰可读。
- [ ] 参考文献格式统一，核心方法和数据来源均有引用。
- [ ] AI 使用情况表如实披露 Codex/Claude/LLM 辅助范围。
- [ ] 查重率和正文字符数满足官方/赛区要求。
- [ ] 原始数据授权边界已检查；提交包默认不含 `data/raw/`。
