# 关键研究决策台账

## 2026-04-20 当前已确认事项

### 1. 题目主线

- 从“数字经济”收紧到“数字普惠金融”
- 原因：PKU 指数与现有文献、数据和识别叙事更一致

### 2. 结果变量

- 主结果变量：`碳排放强度`
- 稳健性结果：`碳排放总量`
- 原因：主线更贴近当前城市样本的文献习惯与 DML 叙事，同时保留总量作为减排直觉检验

### 3. 样本窗口

- 当前主线采用：`2019-2023`
- 原因：2019 可作为政策前基期，PKU 到 2023，CMCC 已能支撑该窗口

### 4. 政策文本模块定位

- 机制项 + 调节项
- 不作为主处理变量
- 不做简单情绪评分

## 历史未决事项（已由 2026-05-03 决策覆盖）

### 1. 人口控制变量口径

- 当前字段：`population_control_candidate`
- 风险：跨年混用 `户籍人口 / 常住人口 / 年平均人口`
- 最新决定：不进入主回归，只作为稳健性/敏感性控制变量

### 2. 当前样本是否接受为主分析样本

- 当前 ready 样本：`294` 城 / `1456` 行
- 最新决定：接受当前 `2019-2023` 样本作为当前主分析样本
- 仍需披露的边界：
  - `CMCC` 本地不覆盖 `营口 / 三沙 / 儋州`
  - 一批自治州、盟、地区在核心控制变量上系统性缺失

## 2026-04-22 新增执行决策

### 3. 首轮主回归采用方案 B 执行

- 当前首轮正式 DML 主回归按以下控制集执行：
  - `gdp_total`
  - `secondary_industry_share`
  - `fiscal_expenditure`
- `population_control_candidate` 暂不进入主规格

### 4. 首轮主回归结果（阶段性）

- 样本：`294` 城 / `1456` 行
- ATE = `-0.0540`
- 95% CI = `[-0.0951, -0.0130]`
- p-value = `0.0099`
- Cross-fitting：`GroupKFold(pku_city_code)`
- 协方差估计：`cluster(pku_city_code)`

说明：

- 该结果是当前数据准备与控制集方案下的首轮正式估计
- 可作为后续稳健性与论文表格整理的基线
- 但不等于最终定稿结果

### 5. 同规格稳健性结果已补跑

- 在相同控制集、相同 `GroupKFold(pku_city_code)` 与 `cluster(pku_city_code)` 设定下，
  将结果变量替换为 `co2_emission_total` 后，得到：
  - ATE = `-129.93`
  - 95% CI = `[-224.18, -35.67]`
  - p-value = `0.0069`

含义：

- 主结果（碳排放强度）与稳健性结果（碳排放总量）方向一致
- 这为“数字普惠金融具有减排效应”的当前叙述提供了更强的阶段性支持

### 6. 候选异质性链路已技术跑通

- 已在候选特征集 `gdp_total + secondary_industry_share + fiscal_expenditure` 上完成首轮技术性 CATE 运行
- 当前候选 CATE 汇总：
  - `cate_mean = -0.0516`
  - `cate_std = 0.0648`
  - `cate_q25 = -0.0699`
  - `cate_median = -0.0323`
  - `cate_q75 = -0.0196`

说明：

- 该结果当前只用于确认 `05_heterogeneity.py` 的技术链路已打通
- 不能直接上升为论文 headline 异质性结论
- 是否将当前特征集作为正式异质性解释变量，仍属于研究设计决定

## 2026-05-02 新增执行状态

### 7. 政策文本 seed 机制候选回归已跑通

- 已将首批中央政策 seed 的规则代理分数合并为 city-year 机制候选变量
- 已完成候选机制 OLS 技术入口，并导出：
  - `outputs/tables/table_05_policy_seed_mechanism_candidate.csv`
  - `outputs/tables/table_05_policy_seed_mechanism_candidate.tex`
- 当前候选机制变量结果：
  - `sum_policy_strength_city_year`: 系数 `10.4758`，95% CI = `[5.0697, 15.8819]`，p-value = `0.0001`
  - `mean_execution_clarity_city_year`: 系数 `26.1894`，95% CI = `[12.6742, 39.7047]`，p-value = `0.0001`
  - `mean_digital_green_synergy_city_year`: 系数 `26.1894`，95% CI = `[12.6742, 39.7047]`，p-value = `0.0001`

说明：

- 该结果只证明政策文本机制变量的“登记—评分—聚合—并表—回归”技术链路已打通
- 由于当前仍是 seed 中央文档和 rule-proxy 分数，该结果不能作为最终论文机制结论
- 是否扩展到完整中央—省级—地级市政策语料，以及是否采用 validated LLM scoring，仍属于后续研究设计与执行任务

### 8. 结果章节骨架与首批图形资产已建立

- 已在 `docs/paper/01_draft.md` 增补“描述事实—基准 DML—稳健性—候选异质性—政策机制候选”的结果章节骨架
- 已新增 `docs/paper/table-figure-inventory.md` 维护表图清单、生成脚本和论文使用边界
- 已新增 `src/25_export_result_figures.py`，可生成：
  - `Figure 1`: 数字普惠金融与碳排放强度年度趋势
  - `Figure 2`: DML 主结果与稳健性估计区间
  - `Figure 3`: 候选 CATE 分布
  - `Figure 4`: 政策文本 seed 机制覆盖与分数快照

说明：

- `Figure 1` 是描述性趋势，不是因果证据
- `Figure 3` 仍是候选异质性技术结果
- `Figure 4` 仍是 seed rule-proxy 政策机制覆盖快照，不是 validated LLM 机制证据，也不是连续政策趋势证据
- `outputs/figures/*` 默认不进入 git；可由脚本复现生成

## 2026-05-03 新增执行状态

### 9. Table 1 描述性统计已建立

- 已将 `src/03_eda.py` 从占位脚本更新为当前候选 DML 样本描述统计导出入口
- 已生成：
  - `outputs/tables/table_01_descriptive_statistics.csv`
  - `outputs/tables/table_01_descriptive_statistics.tex`
- 当前 Table 1 覆盖 `1456` 个 city-year 观测，变量包括：
  - 主结果变量：碳排放强度
  - 稳健性结果变量：碳排放总量
  - 处理变量：数字普惠金融指数
  - 数字金融分项：覆盖广度、使用深度、数字化程度
  - 当前主规格控制变量：地区生产总值、第二产业占比、财政支出
  - 候选控制变量：人口规模

说明：

- 该表服务于论文 Table 1 的描述性统计占位与复现
- `population_control_candidate` 在表中明确标记为“候选控制变量，未锁定”
- 当前样本规模仍不等于最终定稿样本；最终样本/规格确认后需重跑该表

### 10. 论文 v0.1 正文初稿已建立

- 已新增 `docs/paper/02_manuscript_v0_1.md`
- 该稿将当前技术材料整理为连续论文结构，覆盖：
  - 摘要与关键词
  - 引言
  - 文献综述与理论背景
  - 理论机制与阶段性研究假设
  - 数据、变量与样本
  - 研究方法
  - 当前实证结果
  - 讨论、局限性与阶段性结论

说明：

- 该文稿是 `v0.1 技术初稿`，用于后续持续扩写和替换结果
- 文稿中明确保留当前样本边界、人口稳健性定位、异质性分组边界和 seed rule-proxy 政策文本机制边界
- 正式定稿前仍需补充文献引用格式、OLS FE、安慰剂检验、正式异质性分组和 validated LLM 政策文本评分结果

### 11. OLS 双向固定效应候选对照已补充

- 已将 `src/06_robustness.py` 从占位脚本更新为 OLS TWFE 候选稳健性导出入口
- 设定：
  - 处理变量：`digital_inclusive_finance_index`
  - 控制变量：`gdp_total + secondary_industry_share + fiscal_expenditure`
  - 固定效应：城市固定效应 + 年份固定效应
  - 标准误：城市聚类
- 已生成：
  - `outputs/tables/table_06_ols_twfe_candidate.csv`
  - `outputs/tables/table_06_ols_twfe_candidate.tex`
- 当前候选结果：
  - 碳排放强度：系数 `-0.0668`，95% CI = `[-0.1068, -0.0267]`，p-value = `0.0011`
  - 碳排放总量：系数 `48.3482`，95% CI = `[-6.8023, 103.4988]`，p-value = `0.0858`

说明：

- OLS TWFE 是传统线性稳健性参照，不替代 DML 主识别
- 强度口径与 DML 主结果方向一致
- 总量口径没有复制 DML 的负向显著结果，后续需要继续补充安慰剂检验、学习器替换和变量口径审查

### 12. Figure 2 / Figure 4 呈现口径已修正

- `Figure 2` 保留在正文结果候选中，但已增加 ATE、95% CI 和 p-value 注释，明确两个结果变量使用各自量纲
- `Figure 4` 不再呈现为“年度趋势图”，因为当前 seed 政策文本只在样本窗口内形成稀疏覆盖
- `Figure 4` 输出文件已改为：
  - `outputs/figures/figure_04_policy_seed_mechanism_snapshot.pdf`
- `outputs/figures/figure_04_policy_seed_mechanism_trends.pdf` 已作为过时生成物清理

写作决定：

- `Table 2` 和 `Figure 2` 可以进入结果章节
- `Table 5` 和 `Figure 4` 当前不建议进入正文主结果表图；应作为政策文本机制技术附录或模块说明，直到完成完整语料和 validated LLM scoring

### 13. DML 残差置换安慰剂检验已补充

- 已扩展 `src/06_robustness.py`，在 OLS TWFE 之外导出 DML placebo 候选稳健性结果
- 已新增 DML residualization helper，支持复用交叉拟合残差进行 residual-permutation placebo
- 已生成：
  - `outputs/tables/table_07_dml_placebo_candidate_summary.csv`
  - `outputs/tables/table_07_dml_placebo_candidate_summary.tex`
  - `outputs/tables/table_07_dml_placebo_candidate_distribution.csv`
  - `outputs/figures/figure_05_dml_placebo_distribution.pdf`
- 当前候选结果：
  - 真实 ATE = `-0.0541`
  - placebo 均值 = `0.0009`
  - placebo 标准差 = `0.0183`
  - placebo 2.5% / 97.5% 分位数 = `[-0.0351, 0.0359]`
  - 500 次置换经验 p-value = `0.0040`

说明：

- 当前真实 ATE 位于随机置换分布尾部，支持主结果不是由随机处理变量排列产生
- 该结果仍是当前稳健性证据；若后续调整人口稳健性、样本补源或 DML 规格，需同步重跑

### 14. DML 学习器替换候选稳健性已补充

- 已扩展 `src/06_robustness.py`，导出 DML nuisance 学习器替换检验
- 已生成：
  - `outputs/tables/table_08_dml_learner_replacement_candidate.csv`
  - `outputs/tables/table_08_dml_learner_replacement_candidate.tex`
- 当前候选结果：
  - GradientBoosting baseline: ATE = `-0.0541`，95% CI = `[-0.0952, -0.0130]`，p-value = `0.0098`
  - RandomForest replacement: ATE = `-0.0383`，95% CI = `[-0.0761, -0.0005]`，p-value = `0.0472`
  - ExtraTrees replacement: ATE = `-0.0393`，95% CI = `[-0.0775, -0.0012]`，p-value = `0.0432`

说明：

- 三组学习器下 ATE 均为负，说明主结果方向对 nuisance learner 替换具有一定稳定性
- 替换学习器后的效应绝对值有所收缩，显著性接近 5% 临界值，因此写作时应表述为“方向稳定但强度存在一定模型敏感性”
- 若后续调整人口稳健性、样本补源或主学习器设定，需同步重跑

### 15. 当前结论证据链汇总表已建立

- 已新增 `src/26_export_evidence_synthesis.py`
- 已生成：
  - `outputs/tables/table_09_current_evidence_synthesis.csv`
  - `outputs/tables/table_09_current_evidence_synthesis.tex`
- `Table 9` 汇总：
  - DML 主结果
  - 替换结果变量
  - OLS TWFE 强度与总量口径
  - DML 安慰剂检验
  - DML 学习器替换
  - 候选异质性
  - 政策文本机制边界

说明：

- `Table 9` 不是新增模型结果，而是当前证据链写作汇总
- 可用于论文结论段落、答辩展示和内部决策沟通
- 当前综合判断：主效应证据较明确，稳健性总体支持但存在口径与模型敏感性；异质性与政策机制仍需后续锁定和补强

## 对写作的直接影响

1. 摘要中可以直接写“已形成 2019—2023 年城市级 DML 主分析样本”
2. 人口变量不得写入主回归控制集，只能写为稳健性/敏感性变量
3. 当前样本已被接受为当前主分析样本，但仍需披露数据缺口和口径边界；如后续补源或稳健性口径变化，应同步重跑相关表图
4. 政策文本机制目前只能写成 seed 技术候选证据或附录证据，不能写成最终机制发现
5. 当前首批图形可用于论文结构占位和结果沟通，但最终定稿前需随最终样本、规格和机制语料重跑
6. 当前 Table 1 可用于论文描述统计占位，但最终定稿前需随最终样本和变量口径重跑
7. `02_manuscript_v0_1.md` 可以作为正式论文写作底稿继续扩写，但不能替代最终结果锁定流程
8. OLS TWFE 对照已经可写入稳健性章节，但必须说明它是候选线性基准参照且总量口径与 DML 存在差异
9. 当前政策文本 seed 表图只用于技术附录，不作为正文主结果或最终机制证据
10. Placebo 检验可以写入稳健性章节，但需标注为 residual-permutation 候选检验
11. 学习器替换检验可以写入稳健性章节，但需说明效应强度对学习器存在一定敏感性
12. `Table 9` 可以作为结论证据链汇总使用，但不能替代各模型结果表
13. `Table 10` / `Figure 6` 是正式异质性分组摘要，但仍需标注基于当前 CATE 候选估计

### 16. 2026-05-03 研究设计口径最终同步

- 题目：确认修改为“‘双碳’战略下数字普惠金融的碳减排效应：基于中国地级市面板的双重机器学习因果推断与政策文本机制分析”。
- 主结果：确认使用 `co2_emission_intensity`（碳排放强度）。
- 样本：接受当前 `2019-2023`、`294` 城、`1456` 个 city-year 样本作为当前主分析样本。
- 人口变量：`population_control_candidate` 不进入主回归，仅作为稳健性/敏感性控制变量。
- 异质性：正式 headline 维度确认为区域、经济发展水平、产业结构。
- 政策文本：正文突出方法创新；当前 seed rule-proxy 结果暂放附录或技术说明，不作为正文主结果或最终 validated LLM 机制证据。

写作影响：

- 后续文稿应避免继续使用“数字经济”作为题目处理变量口径，除非是在引言中描述国家战略背景。
- 主回归表述统一为“不含人口变量”的主规格；人口变量只可在稳健性段落出现。
- 异质性章节应从 CATE 技术预检查转向三类正式分组结果。
- 政策文本模块可作为创新点写入正文方法，但当前 Table 5 / Figure 4 应归入附录或技术附录。

### 17. 人口变量敏感性稳健性已补充

- 已新增 `src/28_export_population_sensitivity.py`，导出：
  - `outputs/tables/table_11_population_sensitivity_robustness.csv`
  - `outputs/tables/table_11_population_sensitivity_robustness.tex`
- 设定：在 DML 主结果变量 `co2_emission_intensity` 下，对比：
  - 主规格：`gdp_total + secondary_industry_share + fiscal_expenditure`
  - 人口敏感性规格：主规格控制集 + `population_control_candidate`
- 当前结果：
  - 主规格 ATE = `-0.0541`，95% CI = `[-0.0952, -0.0130]`，p-value = `0.0098`
  - 加入人口后 ATE = `-0.0180`，95% CI = `[-0.0613, 0.0254]`，p-value = `0.4172`
  - 相对主规格变化 = `0.0361`

说明：

- 人口变量加入后估计方向仍为负，但效应绝对值明显收缩且不显著
- 这支持“人口变量不进主回归，只作为稳健性/敏感性”的设计决定
- 论文写作必须保留口径敏感性说明，不能只报告主规格显著结果而忽略 Table 11

### 18. 异质性组间差异诊断已补充

- 已新增 `src/29_export_heterogeneity_group_differences.py`，导出：
  - `outputs/tables/table_12_heterogeneity_group_differences.csv`
  - `outputs/tables/table_12_heterogeneity_group_differences.tex`
- 设定：在 `Table 10` 的 CATE 分组摘要基础上，先将 city-year CATE 折算为城市层面 CATE 均值，再对组间均值差异做 bootstrap 诊断。
- 当前主要结果：
  - 经济发展水平：高经济发展水平组 - 低经济发展水平组差异 = `0.0631`，p ≈ `0.0000`，低经济发展水平组 CATE 更负。
  - 区域：东部—西部差异 = `0.0292`，p ≈ `0.0000`；东部—东北差异 = `0.0459`，p ≈ `0.0000`；中部—西部差异 = `0.0224`，p ≈ `0.0047`；中部—东北差异 = `0.0392`，p ≈ `0.0003`。
  - 产业结构：高第二产业占比组 - 低第二产业占比组差异 = `0.0168`，p ≈ `0.0032`，低第二产业占比组 CATE 更负。

说明：

- `Table 12` 是城市层面 bootstrap 诊断，用于增强异质性叙述。
- 它不等同于重新估计分组 DML，也不应写成“机制已被严格证明”。
- 写作可表述为：当前异质性诊断显示，低经济发展水平城市以及西部、东北等区域的估计减排效应更强，提示数字普惠金融碳减排效应存在发展阶段和区域条件依赖性。

### 19. 政策文本 LLM 评分验证框架已补充

- 已新增 `src/30_prepare_policy_llm_scoring_batch.py`，导出：
  - `data/interim/policy_text/policy_llm_scoring_batch_seed.jsonl`
  - `data/interim/policy_text/policy_llm_score_review_template_seed.csv`
- 已新增 `src/31_validate_policy_llm_scores.py`，导出：
  - `data/interim/policy_text/policy_llm_validation_detail_seed.csv`
  - `outputs/tables/table_13_policy_llm_validation_readiness.csv`
  - `outputs/tables/table_13_policy_llm_validation_readiness.tex`
- 当前 Table 13 结果：
  - 登记文档数 = `3`
  - 已评分行数 = `0`
  - 人工复核行数 = `0`
  - 验证就绪行数 = `0`
  - readiness_status = `not_ready`

说明：

- 这一步推进的是 validated LLM scoring 的可复现框架，不虚构 LLM 分数。
- 当前政策文本机制仍只能写作“方法创新 + 技术附录候选”，不能写成最终 validated LLM 机制证据。
- 后续若要将政策文本机制推进为正文机制结果，需要填充 LLM 分数、记录模型/运行批次、完成抽样人工复核，并重新运行 `src/31_validate_policy_llm_scores.py` 与后续机制并表/回归。
