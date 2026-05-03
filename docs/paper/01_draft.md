# “双碳”战略下数字普惠金融的碳减排效应：基于中国地级市面板的双重机器学习因果推断与政策文本机制分析

## 摘要

在“双碳”战略背景下，数字普惠金融是否能够推动城市低碳转型，是一个兼具国家战略意义和经验识别难度的重要问题。本文基于中国地级市面板数据，构建数字普惠金融与城市碳排放结果变量的匹配样本，尝试识别数字普惠金融的碳减排效应及其异质性机制。处理变量采用北京大学数字普惠金融指数，主结果变量采用城市碳排放强度，稳健性结果保留城市碳排放总量。方法上，本文以双重机器学习为主识别工具，并使用因果森林开展异质性分析；正式异质性维度确认围绕区域、经济发展水平和产业结构展开。同时构建政策文本机制模块，设计从中央—省级—地级市多层级政策文件中提取政策强度、执行明确性和数字绿色协同度，用于解释数字普惠金融减排效应的差异来源。当前数据准备结果显示，在 2019—2023 年窗口内，已形成 `294` 个城市、`1456` 个 city-year 的 DML 输入样本，并已完成首轮 DML 主回归、总量稳健性、正式异质性分组与 seed 政策机制技术运行。研究的主要边界在于人口变量不进入主回归、只作为稳健性/敏感性变量，政策文本分数仍是 seed rule-proxy 而非 validated LLM scoring；政策文本方法创新可在正文说明，但当前 seed 结果应暂放附录或技术说明。

## 关键词

数字普惠金融；碳排放强度；双重机器学习；城市面板；政策文本分析

## 一、研究问题

本文当前聚焦以下核心问题：

1. 数字普惠金融发展是否显著降低城市碳排放强度？
2. 这一影响在不同城市之间是否存在显著异质性？
3. 政策环境是否会强化或削弱数字普惠金融的减排效应？

## 二、当前已确认设计

### 0. 论文题目

- 当前题目：“双碳”战略下数字普惠金融的碳减排效应：基于中国地级市面板的双重机器学习因果推断与政策文本机制分析
- 题目主线：从宽泛“数字经济”明确收紧为“数字普惠金融”，与 PKU-DFIIC 处理变量保持一致。

### 1. 研究对象与时间范围

- 研究对象：中国地级市
- 主样本窗口：`2019-2023`
- 样本状态：接受当前 `294` 城、`1456` 个 city-year 的 2019—2023 样本作为当前主分析样本；仍需在局限性中披露缺口城市与数据口径边界。

### 2. 变量设计

- 处理变量：`digital_inclusive_finance_index`
- 主结果变量：`co2_emission_intensity`
- 稳健性结果：`co2_emission_total`
- 人口变量：`population_control_candidate` 不进入主回归，仅用于稳健性/敏感性分析。

### 3. 方法路线

- 主识别：DML
- 异质性：Causal Forest + 正式分组摘要；headline 维度为区域、经济发展水平、产业结构
- 政策文本模块：正文讲方法创新，当前 seed 结果暂放附录/技术说明，定位为机制项 + 调节项接口

## 三、当前数据与样本状态

### 1. 已完成的数据准备

- 已完成 `CMCC -> PKU` 高置信候选映射
- 已完成 `PKU 2019-2023` 城市面板标准化
- 已完成一版核心控制变量抽取：
  - `gdp_total`
  - `secondary_industry_share`
  - `population_raw`（不进主回归，仅稳健性/敏感性候选）
  - `fiscal_expenditure`
- 已完成一版 `PKU + CMCC + 核心控制变量` 主建模候选底表
- 已完成一版 `DML candidate input`
- 已完成政策文本 source manifest、registry template、city-year template
- 已完成首批中央政策 seed registry、seed rule-proxy scoring 和 seed mechanism panel

### 2. 当前可用样本规模

根据当前最新数据准备结果：

- PKU 总城市数：`338`
- 有 CMCC 结果变量城市数：`335`
- 有核心控制变量城市数：`296`
- 可直接进入 DML 候选输入的样本：`294` 城，`1456` 行

## 四、当前已完成工作总览

截至目前，项目已完成的工作可分为五条主线：

### 1. 数据准备主线

- `CMCC` 城市日度碳排放数据已完成年度化处理
- `PKU` 城市面板已完成标准化
- `CMCC -> PKU` 城市映射、样本缺口与边界说明已完成
- 第一批核心控制变量已完成抽取和候选底表构建

### 2. 主回归主线

- `04_dml_main.py` 已从空壳推进为可运行主回归入口
- 首轮 DML 主结果已完成
- 总量稳健性结果已完成
- `Table 2` 的 `.csv + .tex` 已导出

### 3. 异质性主线

- 异质性候选输入表已完成
- 候选特征集相关性诊断已完成
- 候选 CATE 技术运行已完成
- 正式异质性维度已确认为区域、经济发展水平、产业结构
- `Table 3`、`Table 4` 已导出
- `Table 10` 与 `Figure 6` 已导出，作为正式异质性分组摘要
- `Table 12` 已导出，作为城市层面 bootstrap 组间差异诊断

### 4. 政策文本机制主线

- 政策文本抓取/登记/聚合的数据结构已完成
- 首批中央层面政策 seed 文档已进入 registry
- 基于规则代理分数的 seed mechanism panel 已生成
- seed mechanism 字段已并回主建模候选面板
- 首轮候选机制回归技术入口已跑通
- `Table 5` 的候选机制回归 `.csv + .tex` 已导出
- LLM 评分 payload、人工/LLM 复核模板与验证就绪度表已建立，`Table 13` 显示当前仍为 `not_ready`

### 5. 论文写作与决策追踪主线

- 论文主稿 `docs/paper/01_draft.md` 已建立并持续维护
- 关键决策台账 `docs/paper/decision-log.md` 已建立并持续维护
- 当前题目、主回归结果、稳健性结果、正式异质性分组和 seed 机制技术状态均已同步进文稿


## 四点五、截至 2026-05-03 的项目同步进展

本轮同步完成以下事项：

1. 论文题目已确认并同步为“‘双碳’战略下数字普惠金融的碳减排效应：基于中国地级市面板的双重机器学习因果推断与政策文本机制分析”。
2. 主结果口径固定为碳排放强度，碳排放总量保留为稳健性结果。
3. 当前 `2019-2023`、`294` 城、`1456` 个 city-year 样本已作为当前主分析样本继续推进。
4. 人口变量明确不进入主回归，仅作为后续稳健性/敏感性检验。
5. 异质性主线已从“CATE 技术预检查”推进到“区域 + 经济发展水平 + 产业结构”三类正式分组摘要，并导出 `Table 10` / `Figure 6` / `Table 12`。
6. 政策文本模块在正文中保留为方法创新，当前 seed rule-proxy 结果暂放附录或技术说明。

当前项目已经具备论文初稿继续扩写的核心证据链：描述统计、DML 主结果、替换结果变量、OLS TWFE 对照、安慰剂检验、学习器替换、人口变量敏感性、正式异质性分组与组间差异诊断、政策文本机制接口和 LLM 评分验证框架。下一步重点不再是等待数据，而是解释人口敏感性结果、实际执行并人工复核政策文本 LLM scoring，并将现有结果整合为完整正文。

## 五、当前写作边界

以下内容已经明确，但需要在论文中谨慎表述：

- `population_control_candidate` 不进入主回归，只能作为稳健性/敏感性变量使用
- 当前 `2019-2023`、`294` 城、`1456` 个 city-year 样本已作为当前主分析样本接受；但仍需披露其候选来源、缺口城市和数据口径边界
- `CMCC` 在本地数据中仍缺 `营口 / 三沙 / 儋州`
- 当前政策文本分数仍以 `seed_rule_proxy` 为主，只能作为附录/技术候选机制变量，不能直接写成最终 validated LLM 机制证据
- `Table 13` 当前为 `not_ready`，只说明 LLM 评分与人工复核流程已可执行，不说明政策文本机制已经验证完成

## 六、当前建议的主回归控制集

从样本稳定性和口径风险平衡角度，当前建议主回归优先采用：

- `gdp_total`
- `secondary_industry_share`
- `fiscal_expenditure`

而将 `population_control_candidate` 明确排除在主回归之外，仅保留为稳健性或敏感性控制变量。

## 七、在当前已有数据下，后续仍可继续推进的工作

在不新增数据源的情况下，以下工作仍然可以继续开展：

1. 主回归结果的进一步表格化、文字化解释与图示整理
2. 稳健性结果的进一步扩展和对比呈现，尤其是人口敏感性带来的效应收缩
3. 围绕区域、经济发展水平和产业结构继续补充分组差异解释，将 `Table 12` 作为诊断证据而非最终机制证明
4. 政策文本 seed 机制变量的技术性回归结果解释与附录边界说明
5. 论文摘要、研究设计、变量说明和阶段性结果章节的持续补写

也就是说，**当前项目并没有因为数据不足而停滞**。在现有数据下，主回归、稳健性、正式异质性和 seed 机制链路都能继续往前推进。

但以下事项若要进入“最终论文定稿口径”，仍需要进一步确认或补源：

1. `营口 / 三沙 / 儋州` 是否需要额外补源
2. 政策文本是否从 seed 中央文档扩展到更完整的中央—省级—地级市语料
3. validated LLM scoring 是否完成真实评分、抽样人工校验与一致性记录

## 八、下一步待补

1. 围绕区域、经济发展水平、产业结构三类正式异质性分组补充理论解释，并审查 `Table 12` 是否足以支撑正文表述
2. 视需要决定是否为 `营口 / 三沙 / 儋州` 补源
3. 将当前结果进一步整理为论文正文中的“基准回归—稳健性—正式异质性—政策文本方法创新/附录机制候选”叙述链条

## 八点五、论文 v0.1 初稿状态

已新增 `docs/paper/02_manuscript_v0_1.md` 作为可连续扩写的论文正文初稿。该文稿已经包含：

- 摘要与关键词
- 引言
- 文献综述与理论背景
- 理论机制与阶段性研究假设
- 数据来源、变量与样本
- DML、异质性与政策文本机制方法说明
- 当前实证结果
- 讨论、局限性与阶段性结论

使用边界：

- 该文稿是 `v0.1 技术初稿`，不是最终定稿
- 其中所有样本、主规格、异质性和政策机制表述均遵守当前研究设计边界：人口不进主回归，政策文本 seed 结果不进正文主结果
- 后续人口敏感性解释、异质性理论解释和 validated LLM 政策文本评分完成后，需要同步改写该文稿

## 九、当前首轮主回归结果（阶段性）

基于当前主样本与控制集方案 B：

- 样本：`294` 城，`1456` 个 city-year
- 处理变量：`digital_inclusive_finance_index`
- 主结果变量：`co2_emission_intensity`
- 控制变量：`gdp_total + secondary_industry_share + fiscal_expenditure`
- 方法：部分线性 DML（`5-fold cross-fitting`，nuisance models 为 `GradientBoostingRegressor`）

当前首轮估计结果显示：

- ATE = `-0.0540`
- 标准误 = `0.0210`
- 95% CI = `[-0.0951, -0.0130]`
- p-value = `0.0099`
- Cross-fitting = `GroupKFold(pku_city_code)`
- 协方差估计 = `cluster(pku_city_code)`

这一结果的方向与“数字普惠金融有助于降低城市碳排放强度”的理论预期一致。
但必须强调：

- 这仍是首轮主回归结果，不是最终论文定稿结果
- 当前仍需补充人口敏感性、差异检验与正式结果表述润色
- 人口变量已确认不进入主回归，因此该结果对应的是“不含人口变量”的方案 B 主规格阶段性结果

## 十、当前稳健性结果（阶段性）

在同一控制集与同一分组交叉拟合/聚类稳健口径下，将结果变量替换为 `co2_emission_total` 后，首轮稳健性结果显示：

- ATE = `-129.93`
- 标准误 = `48.09`
- 95% CI = `[-224.18, -35.67]`
- p-value = `0.0069`

这一结果说明，在当前主样本与当前控制集下，数字普惠金融的提升不仅对应碳排放强度下降，也对应碳排放总量下降，方向与主结果一致。
但该结果同样属于首轮阶段性估计，后续仍需结合稳健性扩展、异质性分析和正式写作口径进一步审视。

已补充候选 OLS 双向固定效应对照 `Table 6`。该表使用相同处理变量与控制变量，并加入城市固定效应、年份固定效应和城市聚类标准误。当前候选结果为：

- 碳排放强度：系数 `-0.0668`，95% CI = `[-0.1068, -0.0267]`，p-value = `0.0011`
- 碳排放总量：系数 `48.3482`，95% CI = `[-6.8023, 103.4988]`，p-value = `0.0858`

解释边界：OLS TWFE 是候选稳健性参照，不替代 DML 主识别。当前强度口径与 DML 主结果方向一致；总量口径在 TWFE 下未复制 DML 的负向显著结果，提示后续需要继续补充安慰剂检验、学习器替换和变量口径审查。

已补充 DML 残差置换安慰剂检验 `Table 7` 和 `Figure 5`。当前版本对主结果变量 `co2_emission_intensity` 进行 `500` 次 residual-permutation placebo：真实 ATE 为 `-0.0541`，placebo 分布均值为 `0.0009`，标准差为 `0.0183`，2.5% 与 97.5% 分位数分别为 `-0.0351` 和 `0.0359`，经验 p-value 为 `0.0040`。这说明当前真实估计值位于随机置换分布尾部，支持主结果并非由随机处理变量排列产生。

解释边界：该安慰剂检验是当前稳健性证据；若后续调整人口稳健性、样本补源或 DML 规格，需同步重跑。


已补充人口变量敏感性稳健性检验 `Table 11`。该表在 DML 主结果变量 `co2_emission_intensity` 下对比“不含人口变量”的主规格与“加入 `population_control_candidate`”的敏感性规格。当前结果为：

- 主规格：ATE = `-0.0541`，95% CI = `[-0.0952, -0.0130]`，p-value = `0.0098`；
- 加入人口变量后：ATE = `-0.0180`，95% CI = `[-0.0613, 0.0254]`，p-value = `0.4172`；
- 相对主规格变化：`0.0361`。

解释边界：人口变量加入后估计方向仍为负，但效应绝对值明显收缩且不显著。这并不改变“人口变量不进主回归”的设计决定，反而说明人口口径对结果有明显敏感性。论文写作应将 `Table 11` 放在稳健性边界中，谨慎表述为“主规格结果较明确，但人口口径敏感性提示结论需要保留控制变量口径边界”。

已补充 DML 学习器替换候选稳健性检验 `Table 8`。在保持相同样本、处理变量、结果变量、控制变量、城市分组交叉拟合和城市聚类标准误的条件下，替换 nuisance model 后的结果为：

- GradientBoosting baseline：ATE = `-0.0541`，95% CI = `[-0.0952, -0.0130]`，p-value = `0.0098`
- RandomForest replacement：ATE = `-0.0383`，95% CI = `[-0.0761, -0.0005]`，p-value = `0.0472`
- ExtraTrees replacement：ATE = `-0.0393`，95% CI = `[-0.0775, -0.0012]`，p-value = `0.0432`

这说明主结果的负向方向在不同树模型学习器下保持一致，但随机森林与极端随机树规格下显著性接近 5% 临界值，最终表述应写成“方向稳定、强度略有变化”，而不是过度强调估计大小完全一致。

已新增当前结论证据链汇总 `Table 9`。该表不是新增模型结果，而是将 DML 主结果、替换结果变量、OLS TWFE 对照、安慰剂检验、学习器替换、异质性和政策文本机制边界统一整理为写作与答辩用证据链。当前综合判断为：主效应证据较明确，稳健性总体支持但存在口径与模型敏感性；异质性维度已锁定并开始输出正式分组摘要；政策文本机制仍是技术附录证据。

## 十一、当前异质性运行状态（阶段性）

在候选异质性特征集

- `gdp_total`
- `secondary_industry_share`
- `fiscal_expenditure`

下，已完成一版技术性的 CATE 运行准备与首轮候选估计。当前结果仅用于确认异质性建模链路已打通，不直接作为论文 headline 结论。当前候选 CATE 汇总显示：

- `nobs = 1456`
- `cate_mean = -0.0516`
- `cate_std = 0.0648`
- `cate_q25 = -0.0699`
- `cate_median = -0.0323`
- `cate_q75 = -0.0196`

这说明在当前技术实现下，CATE 估计总体方向与主回归保持一致，即数字普惠金融的提升对应更低的碳排放强度。最新研究设计已将 headline 异质性维度锁定为区域、经济发展水平和产业结构；因此当前 CATE 分布只作为技术基础，正式论文解释应转向三类分组结果。


### 11.1 正式异质性分组摘要（首轮）

已新增 `Table 10` 和 `Figure 6`，将当前 CATE 候选估计按三类已确认维度进行分组：

- 区域：东部、中部、西部、东北
- 经济发展水平：按城市 2019—2023 年 GDP 均值中位数划分为高/低组
- 产业结构：按城市 2019—2023 年第二产业占比均值中位数划分为高/低组

当前首轮分组结果显示：

- 区域维度：东部 CATE 均值 `-0.0358`，中部 `-0.0425`，西部 `-0.0635`，东北 `-0.0819`；
- 经济发展水平维度：高经济发展水平组 CATE 均值 `-0.0206`，低经济发展水平组 `-0.0831`；
- 产业结构维度：高第二产业占比组 CATE 均值 `-0.0432`，低第二产业占比组 `-0.0601`。

写作边界：该表是基于当前 CATE 候选估计的分组摘要，近似置信区间用于描述组内 CATE 均值的不确定性，不等同于严格的 subgroup significance test。当前可谨慎写为“低经济发展水平、西部/东北等组的估计减排效应更强”，但不能写成最终因果机制已经被完全证明。

### 11.2 异质性组间差异诊断（首轮）

已新增 `Table 12`，在 `Table 10` 的三类正式异质性分组基础上，将 city-year CATE 先折算为城市层面 CATE 均值，再在城市层面进行 bootstrap 组间差异诊断。当前主要结果为：

- 区域维度：东部—西部差异 `0.0292`，p ≈ `0.0000`；东部—东北差异 `0.0459`，p ≈ `0.0000`；中部—西部差异 `0.0224`，p ≈ `0.0047`；中部—东北差异 `0.0392`，p ≈ `0.0003`。差异方向提示西部和东北组 CATE 更负。
- 经济发展水平维度：高经济发展水平—低经济发展水平差异 `0.0631`，p ≈ `0.0000`，提示低经济发展水平城市 CATE 更负。
- 产业结构维度：高第二产业占比—低第二产业占比差异 `0.0168`，p ≈ `0.0032`，提示低第二产业占比组 CATE 更负。

解释边界：`Table 12` 是“城市层面 CATE 均值 bootstrap 组间差异诊断”，用于增强异质性叙述，不等同于重新估计分组 DML，也不等同于严格证明某一城市类型存在独立机制。论文正文可以把它作为“异质性差异具有统计诊断支持”的证据，但仍需配合理论解释和稳健性边界。

## 十二、当前政策机制技术运行状态（阶段性）

当前政策文本机制模块已推进到 seed 级别：

- 已建立 source manifest
- 已建立 document registry template
- 已建立 city-year score template
- 已写入首批中央层面政策 seed 文档
- 已基于规则代理分数生成 seed mechanism panel
- 已将 seed mechanism 字段并回主建模候选面板
- 已完成候选机制回归技术入口
- 已导出政策文本 seed 机制候选结果 `Table 5`
- 已导出 LLM 评分 payload、人工/LLM 复核模板与验证就绪度表 `Table 13`

因此，政策文本机制链路当前的状态应表述为：

> 已完成“真实入口 + seed 机制代理变量 + 可并表面板 + LLM 评分/复核模板”的技术准备，但尚未完成真实 LLM 评分、人工复核与完整政策语料，因此不能直接作为最终论文机制结论。

当前 `Table 5` 的 seed 机制候选回归只用于验证政策文本机制变量可以进入模型链路。该表使用首批中央政策文档的规则代理分数，样本量为 `290`，三个候选机制变量的系数均为正且在当前技术规格下显著：

- `sum_policy_strength_city_year`: 系数 `10.4758`，95% CI = `[5.0697, 15.8819]`，p-value = `0.0001`
- `mean_execution_clarity_city_year`: 系数 `26.1894`，95% CI = `[12.6742, 39.7047]`，p-value = `0.0001`
- `mean_digital_green_synergy_city_year`: 系数 `26.1894`，95% CI = `[12.6742, 39.7047]`，p-value = `0.0001`

需要特别强调：这些结果目前只能作为“政策文本机制分析的技术候选证据”。由于政策语料仍是 seed 中央文档，且评分方式仍为透明规则代理而非经过人工校验的 LLM 评分，不能据此直接写出最终机制结论，也不能把上述正系数解释为已验证的因果机制。

当前 `Table 13` 用于记录 LLM 评分验证就绪度。seed 文档已生成 JSONL scoring payload 与人工/LLM 复核模板，但尚未填入真实 LLM 分数或人工复核结果，因此 readiness_status 为 `not_ready`，验证就绪行为 `0/3`。这使政策文本模块从“概念设计”推进到“可执行验证框架”，但仍不能替代正式机制证据。

## 十三、结果章节骨架（待扩写）

本节用于后续论文正文承接。当前结果章节应采用“描述事实—主因果估计—稳健性—正式异质性—政策文本方法创新/附录机制候选”的顺序，避免把技术候选结果写成最终结论。

### 13.1 描述性事实与趋势

可使用 `Table 1` 报告当前 2019—2023 年主分析样本的描述性统计。该表由 `src/03_eda.py` 生成，当前覆盖 `1456` 个 city-year 观测，包括碳排放强度、碳排放总量、数字普惠金融指数及其三个分项、当前主规格控制变量，以及仅用于稳健性/敏感性分析的人口规模变量。

可使用 `Figure 1` 展示 2019—2023 年样本城市数字普惠金融指数与碳排放强度的年度均值趋势。该图只说明变量随时间变化的描述性关系，不能作为因果证据。正文可围绕两个事实展开：

1. 数字普惠金融在样本期内总体上升；
2. 碳排放强度的变化方向可作为后续 DML 因果识别的背景事实。

写作边界：`Table 1` 中的人口规模变量只能表述为稳健性/敏感性候选，不能据此宣布已进入主规格；当前 `1456` 个观测为当前主分析样本规模，最终定稿前仍需随稳健性口径审查重跑。

### 13.2 基准 DML 估计

基准结果对应 `Table 2` 和 `Figure 2`。正文应先交代当前主规格：

- 处理变量为 `digital_inclusive_finance_index`；
- 主结果变量为 `co2_emission_intensity`；
- 控制变量为 `gdp_total + secondary_industry_share + fiscal_expenditure`；
- 交叉拟合按城市分组，标准误按城市聚类。

随后报告阶段性主结果：ATE 为 `-0.0540`，95% 置信区间为 `[-0.0951, -0.0130]`，p-value 为 `0.0099`。当前可谨慎表述为：在方案 B 主规格下，数字普惠金融提升与城市碳排放强度下降显著相关，且 DML 残差化估计支持减排效应方向。

### 13.3 稳健性：替换结果变量

稳健性结果同样对应 `Table 2` 和 `Figure 2`。将结果变量替换为 `co2_emission_total` 后，ATE 为 `-129.93`，95% 置信区间为 `[-224.18, -35.67]`，p-value 为 `0.0069`。当前可以写作：总量口径下的估计方向与强度口径一致，说明基准结论并非仅依赖碳排放强度定义。

但本部分还不是完整稳健性章节。当前已补充 OLS 双向固定效应候选对照 `Table 6`：强度口径系数为 `-0.0668`，95% CI = `[-0.1068, -0.0267]`，p-value = `0.0011`；总量口径系数为 `48.3482`，95% CI = `[-6.8023, 103.4988]`，p-value = `0.0858`。这意味着 OLS TWFE 在强度口径上支持主方向，但在总量口径上没有复制 DML 的负向显著结果。当前还补充了 DML 残差置换安慰剂检验 `Table 7` 和 `Figure 5`：500 次 placebo 的经验 p-value 为 `0.0040`，真实 ATE 位于随机置换分布尾部。`Table 8` 显示，替换为 RandomForest 和 ExtraTrees 后，主结果 ATE 仍为负且在 5% 水平附近显著，说明方向具有一定稳定性。`Table 11` 显示，加入人口变量后 ATE 仍为负但收缩为 `-0.0180` 且不显著，提示人口口径对估计有明显敏感性。后续仍需变量口径审查。

### 13.4 正式异质性分组分析

异质性基础结果对应 `Table 3`、`Table 4` 和 `Figure 3`，正式分组结果对应 `Table 10`、`Table 12` 和 `Figure 6`。当前 CATE 均值为 `-0.0516`，中位数为 `-0.0323`，总体方向与基准 DML 一致。分组摘要显示，区域维度上东北和西部组的 CATE 均值更负；经济发展水平维度上低经济发展水平组的 CATE 均值更负；产业结构维度上低第二产业占比组的 CATE 均值略更负。组间差异诊断进一步显示，低经济发展水平组相对高经济发展水平组的差异最大，东部—西部、东部—东北、中部—西部、中部—东北等区域差异也较明显。

本部分不得提前写成“哪些类型城市必然更强”的最终因果结论。正式版本可将这些差异解释为数字普惠金融减排效应可能具有发展阶段和区域条件依赖性，但必须说明 `Table 10` / `Figure 6` 是基于当前 CATE 候选估计的分组摘要，`Table 12` 是城市层面 bootstrap 诊断，均不等同于重新估计分组 DML。

### 13.5 政策文本机制技术附录候选

政策文本机制候选结果对应 `Table 5`、`Table 13` 和 `Figure 4`。当前模块已经证明政策文本变量可以完成“文档登记—规则代理评分—city-year 聚合—并表—机制候选回归”的技术闭环，并且已建立“LLM scoring payload—人工/LLM 复核模板—验证就绪度表”的可复现验证框架。

正文处理建议：`Table 5`、`Table 13` 和 `Figure 4` 暂不放入主结果章节作为正式机制发现；更适合放在“政策文本机制模块设计”或技术附录中，用来说明机制变量链路与 LLM 验证框架已经跑通。由于尚未完成完整中央—省级—地级市政策语料和真实 validated LLM scoring，不能将 `Table 5` 写成最终机制发现，也不能把 `Figure 4` 解释为政策趋势图。当前 `Figure 4` 已改为 seed 覆盖与分数快照，专门避免把稀疏 seed 文档误画成连续时间趋势。

### 13.6 当前表图资产

当前表图清单维护在 `docs/paper/table-figure-inventory.md`。`Table 1` 与图形可由以下命令重新生成：

```bash
python3 src/03_eda.py
python3 src/06_robustness.py
python3 src/28_export_population_sensitivity.py
python3 src/25_export_result_figures.py
python3 src/27_export_heterogeneity_groups.py
python3 src/29_export_heterogeneity_group_differences.py
python3 src/30_prepare_policy_llm_scoring_batch.py
python3 src/31_validate_policy_llm_scores.py
python3 src/26_export_evidence_synthesis.py
```

这些命令会输出：

- `outputs/tables/table_01_descriptive_statistics.csv`
- `outputs/tables/table_01_descriptive_statistics.tex`
- `outputs/tables/table_06_ols_twfe_candidate.csv`
- `outputs/tables/table_06_ols_twfe_candidate.tex`
- `outputs/tables/table_07_dml_placebo_candidate_summary.csv`
- `outputs/tables/table_07_dml_placebo_candidate_summary.tex`
- `outputs/tables/table_07_dml_placebo_candidate_distribution.csv`
- `outputs/tables/table_08_dml_learner_replacement_candidate.csv`
- `outputs/tables/table_08_dml_learner_replacement_candidate.tex`
- `outputs/tables/table_09_current_evidence_synthesis.csv`
- `outputs/tables/table_09_current_evidence_synthesis.tex`
- `outputs/figures/figure_01_digital_finance_carbon_intensity_trends.pdf`
- `outputs/figures/figure_02_dml_effect_intervals.pdf`
- `outputs/figures/figure_03_candidate_cate_distribution.pdf`
- `outputs/figures/figure_04_policy_seed_mechanism_snapshot.pdf`
- `outputs/figures/figure_05_dml_placebo_distribution.pdf`
- `outputs/tables/table_10_heterogeneity_group_summary.csv`
- `outputs/tables/table_10_heterogeneity_group_summary.tex`
- `outputs/figures/figure_06_heterogeneity_groups.pdf`
- `outputs/tables/table_11_population_sensitivity_robustness.csv`
- `outputs/tables/table_11_population_sensitivity_robustness.tex`
- `outputs/tables/table_12_heterogeneity_group_differences.csv`
- `outputs/tables/table_12_heterogeneity_group_differences.tex`
- `outputs/tables/table_13_policy_llm_validation_readiness.csv`
- `outputs/tables/table_13_policy_llm_validation_readiness.tex`
- `outputs/figures/figure_manifest.csv`
