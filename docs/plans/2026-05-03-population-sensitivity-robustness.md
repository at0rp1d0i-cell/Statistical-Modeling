# Population Sensitivity Robustness Implementation Plan

<execution_handoff>
  <executor>codex</executor>
  <primary_mode>solo-execute</primary_mode>
  <alternate_mode>subagent-driven-development</alternate_mode>
  <rule>Execute task-by-task with verification after each task.</rule>
</execution_handoff>

**Goal:** 在不改变主回归控制集的前提下，导出“人口变量仅做稳健性/敏感性”的 DML 对照表，并同步论文初稿。

**Architecture:** 新增独立脚本读取当前 DML 输入表，使用相同 GroupKFold 和城市聚类口径，对比“不含人口变量”的主规格与“加入 `population_control_candidate`”的敏感性规格。结果作为 Table 11 输出，并作为证据链的稳健性补充，而不是替代 Table 2 主结果。

**Tech Stack:** Python, pandas, existing `stat_modeling.modeling.dml.fit_partial_linear_dml`, pytest, Markdown docs.

---

### Task 1: 添加人口敏感性导出脚本与测试

**Files:**
- Create: `src/28_export_population_sensitivity.py`
- Create: `tests/test_export_population_sensitivity.py`

**Steps:**
1. 用当前主结果变量 `co2_emission_intensity`、处理变量 `digital_inclusive_finance_index`、基础控制集 `gdp_total + secondary_industry_share + fiscal_expenditure` 复现基准 DML。
2. 加入 `population_control_candidate` 形成人口敏感性规格。
3. 导出 `outputs/tables/table_11_population_sensitivity_robustness.csv/.tex`。
4. 测试脚本可用临时输入和显式输出路径运行，检查两行规格均存在。

### Task 2: 更新证据链和论文文档

**Files:**
- Modify: `src/26_export_evidence_synthesis.py`
- Modify: `tests/test_export_evidence_synthesis.py`
- Modify: `README.md`
- Modify: `docs/paper/01_draft.md`
- Modify: `docs/paper/02_manuscript_v0_1.md`
- Modify: `docs/paper/decision-log.md`
- Modify: `docs/paper/table-figure-inventory.md`

**Steps:**
1. Table 9 纳入人口敏感性行。
2. 文稿明确：人口变量不进入主回归，Table 11 仅检验敏感性。
3. 表图清单新增 Table 11。
4. README 补充 `src/28_export_population_sensitivity.py`。

### Task 3: 验证、提交、推送

**Commands:**
- `python3 src/28_export_population_sensitivity.py`
- `python3 src/26_export_evidence_synthesis.py`
- `python3 -m pytest -q`
- `python3 -m py_compile $(find src tests -name '*.py' | sort)`
- `git diff --check`
- Lore protocol commit and push.
