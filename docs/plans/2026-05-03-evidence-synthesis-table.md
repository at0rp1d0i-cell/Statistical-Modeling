# Evidence Synthesis Table Implementation Plan

<execution_handoff>
  <executor>codex</executor>
  <primary_mode>subagent-driven-development</primary_mode>
  <alternate_mode>executing-plans</alternate_mode>
  <rule>Execute task-by-task with verification after each task.</rule>
</execution_handoff>

**Goal:** Create a reproducible paper-facing evidence-chain summary that consolidates the current main DML result, robustness checks, heterogeneity signal, and policy-text boundary into one table for manuscript writing.

**Architecture:** Add a thin numbered reporting script, `src/26_export_evidence_synthesis.py`, that reads existing result tables/interim summaries and writes `Table 9` under `outputs/tables/`. The table is descriptive synthesis only; it does not create new estimates or alter research design.

**Tech Stack:** Python, pandas, pytest, existing `stat_modeling.config` paths.

---

### Task 1: Add smoke test

**Files:**
- Create: `tests/test_export_evidence_synthesis.py`

Use synthetic result tables to verify the script creates CSV/TeX outputs and includes rows for DML main, robustness, placebo, learner replacement, heterogeneity, and policy-text boundary.

### Task 2: Implement script

**Files:**
- Create: `src/26_export_evidence_synthesis.py`

Default inputs:

- `outputs/tables/table_02_dml_main_and_robustness.csv`
- `outputs/tables/table_06_ols_twfe_candidate.csv`
- `outputs/tables/table_07_dml_placebo_candidate_summary.csv`
- `outputs/tables/table_08_dml_learner_replacement_candidate.csv`
- `data/interim/modeling/heterogeneity_candidate_cate_summary.csv`
- `outputs/tables/table_05_policy_seed_mechanism_candidate.csv`

Default outputs:

- `outputs/tables/table_09_current_evidence_synthesis.csv`
- `outputs/tables/table_09_current_evidence_synthesis.tex`

### Task 3: Update paper docs

**Files:**
- Modify: `README.md`
- Modify: `docs/paper/table-figure-inventory.md`
- Modify: `docs/paper/01_draft.md`
- Modify: `docs/paper/02_manuscript_v0_1.md`
- Modify: `docs/paper/decision-log.md`

Record Table 9 as a synthesis table for writing, not a new model result.

### Task 4: Verify and commit

Run:

```bash
python3 src/26_export_evidence_synthesis.py
python3 -m pytest -q
python3 -m py_compile $(find src tests -name '*.py' | sort)
git diff --check
```
