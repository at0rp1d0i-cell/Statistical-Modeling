# DML Placebo Robustness Implementation Plan

<execution_handoff>
  <executor>codex</executor>
  <primary_mode>subagent-driven-development</primary_mode>
  <alternate_mode>executing-plans</alternate_mode>
  <rule>Execute task-by-task with verification after each task.</rule>
</execution_handoff>

**Goal:** Add a reproducible candidate placebo robustness check for the current DML main effect and synchronize the manuscript robustness discussion.

**Architecture:** Extend `src/06_robustness.py`, which already owns robustness outputs, to export both the OLS TWFE benchmark and a DML residual-permutation placebo check. The placebo check reuses the DML cross-fitted residualization logic, permutes the residualized treatment 500 times by default, writes a summary table and distribution CSV under `outputs/tables/`, and writes a histogram under `outputs/figures/`.

**Tech Stack:** Python, pandas, numpy, statsmodels, sklearn-backed DML residualization, matplotlib, pytest.

---

### Task 1: Expose DML residualization for placebo reuse

**Files:**
- Modify: `src/stat_modeling/modeling/dml.py`

Add a `DMLResiduals` dataclass and `residualize_partial_linear_dml(...)` helper. Refactor `fit_partial_linear_dml(...)` to use the helper without changing existing results.

### Task 2: Extend robustness smoke coverage

**Files:**
- Modify: `tests/test_robustness_ols_twfe.py`

Run `src/06_robustness.py` with explicit output paths for:

- Table 6 OLS TWFE CSV/TeX;
- Table 7 placebo summary CSV/TeX;
- placebo distribution CSV;
- Figure 5 placebo PDF.

Use a small number of permutations in the test for speed.

### Task 3: Implement placebo exporter

**Files:**
- Modify: `src/06_robustness.py`

Add CLI options for placebo outputs and permutation count. Default to 500 permutations for the project run. Export:

- `outputs/tables/table_07_dml_placebo_candidate_summary.csv`
- `outputs/tables/table_07_dml_placebo_candidate_summary.tex`
- `outputs/tables/table_07_dml_placebo_candidate_distribution.csv`
- `outputs/figures/figure_05_dml_placebo_distribution.pdf`

### Task 4: Update paper-facing docs

**Files:**
- Modify: `README.md`
- Modify: `docs/paper/table-figure-inventory.md`
- Modify: `docs/paper/01_draft.md`
- Modify: `docs/paper/02_manuscript_v0_1.md`
- Modify: `docs/paper/decision-log.md`

Document the placebo as a candidate robustness check, not a final locked robustness conclusion.

### Task 5: Verify and commit

Run:

```bash
python3 src/06_robustness.py
python3 -m pytest -q
python3 -m py_compile $(find src tests -name '*.py' | sort)
git diff --check
```
