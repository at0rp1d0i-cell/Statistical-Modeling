# Heterogeneity Group-Difference Diagnostics Implementation Plan

<execution_handoff>
  <executor>codex</executor>
  <primary_mode>solo-execute</primary_mode>
  <rule>推进整体结果链，先补异质性诊断缺口，再回头打磨论文措辞。</rule>
</execution_handoff>

**Goal:** 在不改变已确认异质性维度的前提下，为区域、经济发展水平、产业结构三类分组补充组间差异诊断表，使论文结果链从“分组均值摘要”推进到“分组差异有诊断证据”。

**Architecture:** 复用 `src/27_export_heterogeneity_groups.py` 已生成的 `heterogeneity_candidate_cate_with_groups.csv`。先将 city-year CATE 折算为城市层面 CATE 均值，再在城市层面按组 bootstrap 组间均值差异。输出仅作为诊断，不替代主 DML ATE，也不等同重新估计分组 DML。

**Tech Stack:** Python, pandas, numpy, existing heterogeneity group utilities, pytest, Markdown docs.

---

### Task 1: 建立组间差异诊断函数

**Files:**
- Modify: `src/stat_modeling/modeling/heterogeneity_groups.py`
- Modify: `tests/test_heterogeneity_groups.py`

**Steps:**
1. 新增城市层面 bootstrap pairwise difference 函数。
2. 覆盖区域、经济发展水平、产业结构三类维度。
3. 输出组均值、组间差异、bootstrap SE、bootstrap CI、近似 p-value 和边界说明。

### Task 2: 添加 Table 12 导出脚本

**Files:**
- Create: `src/29_export_heterogeneity_group_differences.py`
- Create: `tests/test_export_heterogeneity_group_differences.py`

**Steps:**
1. 优先读取 `heterogeneity_candidate_cate_with_groups.csv`。
2. 若该文件不存在，则从 CATE 与 DML 输入表重新附加分组属性。
3. 导出 `outputs/tables/table_12_heterogeneity_group_differences.csv/.tex`。

### Task 3: 更新证据链与论文文档

**Files:**
- Modify: `src/26_export_evidence_synthesis.py`
- Modify: `tests/test_export_evidence_synthesis.py`
- Modify: `README.md`
- Modify: `docs/paper/01_draft.md`
- Modify: `docs/paper/02_manuscript_v0_1.md`
- Modify: `docs/paper/decision-log.md`
- Modify: `docs/paper/table-figure-inventory.md`

**Steps:**
1. Table 9 纳入 Table 12 的异质性差异诊断来源。
2. 文稿中明确 Table 12 的诊断性质和边界。
3. 表图清单新增 Table 12。

### Task 4: 验证、提交、推送

**Commands:**
- `python3 src/27_export_heterogeneity_groups.py`
- `python3 src/29_export_heterogeneity_group_differences.py`
- `python3 src/26_export_evidence_synthesis.py`
- `python3 -m pytest -q`
- `python3 -m py_compile $(find src tests -name '*.py' | sort)`
- `git diff --check`
- Lore protocol commit and push.
