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

## 当前未最终锁定事项

### 1. 人口控制变量口径

- 当前字段：`population_control_candidate`
- 状态：候选变量
- 风险：跨年混用 `户籍人口 / 常住人口 / 年平均人口`
- 当前建议：先不作为主规格锁定控制变量

### 2. 最终主样本是否接受当前候选样本

- 当前 ready 样本：`294` 城 / `1456` 行
- 主要缺口来源：
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
  - `Figure 4`: 政策文本 seed 机制变量年度趋势

说明：

- `Figure 1` 是描述性趋势，不是因果证据
- `Figure 3` 仍是候选异质性技术结果
- `Figure 4` 仍是 seed rule-proxy 政策机制结果，不是 validated LLM 机制证据
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
- 文稿中明确保留候选样本、候选人口控制、候选异质性和 seed rule-proxy 政策文本机制边界
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

## 对写作的直接影响

1. 摘要中可以直接写“已形成 2019—2023 年城市级 DML 候选样本”
2. 但不能把人口变量写成最终锁定控制口径
3. 也不能把当前样本写成最终不可变样本，只能写成“当前主规格候选样本”
4. 政策文本机制目前只能写成 seed 技术候选证据，不能写成最终机制发现
5. 当前首批图形可用于论文结构占位和结果沟通，但最终定稿前需随最终样本、规格和机制语料重跑
6. 当前 Table 1 可用于论文描述统计占位，但最终定稿前需随最终样本和变量口径重跑
7. `02_manuscript_v0_1.md` 可以作为正式论文写作底稿继续扩写，但不能替代最终结果锁定流程
8. OLS TWFE 对照已经可写入稳健性章节，但必须说明它是候选线性基准参照且总量口径与 DML 存在差异
