# Formal Heterogeneity And Title Update Implementation Plan

<execution_handoff>
  <executor>codex</executor>
  <primary_mode>subagent-driven-development</primary_mode>
  <alternate_mode>solo-execute</alternate_mode>
  <rule>Execute task-by-task with verification after each task.</rule>
</execution_handoff>

**Goal:** 将最新研究设计确认同步进项目文稿，并导出区域、经济发展水平、产业结构三类正式异质性分组结果。

**Architecture:** 文档层先记录研究设计覆盖关系，避免旧的“数字经济/题目不改/人口待定/异质性待定”口径继续污染论文。代码层新增一个独立异质性分组导出脚本，读取现有 CATE 与 DML 输入表，按标准地区、城市平均 GDP 中位数、城市平均第二产业占比中位数生成分组摘要表和图形。

**Tech Stack:** Python, pandas, matplotlib, pytest, Markdown documentation.

---

### Task 1: 同步最新研究设计到文档

**Files:**
- Modify: `README.md`
- Modify: `docs/paper/01_draft.md`
- Modify: `docs/paper/02_manuscript_v0_1.md`
- Modify: `docs/paper/decision-log.md`
- Modify: `docs/paper/table-figure-inventory.md`

**Steps:**
1. 将论文题目统一为“‘双碳’战略下数字普惠金融的碳减排效应：基于中国地级市面板的双重机器学习因果推断与政策文本机制分析”。
2. 记录 2026-05-03 最新确认：主结果碳排放强度、2019—2023 当前样本、人口变量只做稳健性、正式异质性维度为区域/经济发展水平/产业结构、政策文本正文讲方法创新且 seed 结果进附录。
3. 移除或改写“题目不改、人口变量未锁定、headline 异质性尚未锁定”等已被覆盖的口径。
4. 运行 `rg` 检查文稿中是否仍有冲突表述。

### Task 2: 增加正式异质性分组函数与测试

**Files:**
- Create: `src/stat_modeling/modeling/heterogeneity_groups.py`
- Create: `tests/test_heterogeneity_groups.py`

**Steps:**
1. 实现省级代码前两位到四大区域的标准映射。
2. 实现城市均值中位数分组：GDP 高/低，第二产业占比高/低。
3. 实现 CATE 与分组变量合并并导出分组均值、分位数、近似均值置信区间。
4. 编写单元测试覆盖区域映射、中位数分组、输出列和样本计数。
5. 运行 `python3 -m pytest tests/test_heterogeneity_groups.py -q`。

### Task 3: 导出 Table 10 与 Figure 6

**Files:**
- Create: `src/27_export_heterogeneity_groups.py`
- Modify: `README.md`
- Modify: `docs/paper/table-figure-inventory.md`
- Modify: `docs/paper/01_draft.md`
- Modify: `docs/paper/02_manuscript_v0_1.md`

**Steps:**
1. 新增脚本读取 `data/interim/modeling/heterogeneity_candidate_cate.csv` 与 `data/interim/modeling/dml_candidate_input_2019_2023.csv`。
2. 输出 `outputs/tables/table_10_heterogeneity_group_summary.csv/.tex`。
3. 输出 `outputs/figures/figure_06_heterogeneity_groups.pdf`。
4. 在文稿中加入 Table 10 / Figure 6 的使用边界：正式分组摘要，但仍基于当前 CATE 候选估计，不能过度解释为最终 subgroup causal test。
5. 运行 `python3 src/27_export_heterogeneity_groups.py`。

### Task 4: 全量验证与 git 管理

**Files:**
- All changed tracked files.

**Steps:**
1. 运行 `python3 -m pytest -q`。
2. 运行 `python3 -m py_compile $(find src tests -name '*.py' | sort)`。
3. 运行 `git diff --check` 与 `git status --short --branch`。
4. 按 Lore protocol commit，并 push `origin main`。
