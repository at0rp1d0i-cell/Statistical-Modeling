# Results Chapter and Figure Assets Implementation Plan

<execution_handoff>
  <executor>codex</executor>
  <primary_mode>subagent-driven-development</primary_mode>
  <alternate_mode>executing-plans</alternate_mode>
  <rule>Execute task-by-task with verification after each task.</rule>
</execution_handoff>

**Goal:** Generate a reproducible first-pass results-to-paper handoff with figure scripts, inventory documentation, and draft results-section structure.

**Architecture:** Keep the implementation lightweight: one numbered reporting script, one smoke test, and documentation updates. The script reads existing project outputs and writes ignored paper artifacts under `outputs/figures/`, while tracked docs describe how those artifacts should be used.

**Tech Stack:** Python, pandas, matplotlib, pytest, existing `stat_modeling.config` paths.

---

### Task 1: Add figure exporter smoke test

**Files:**
- Create: `tests/test_export_result_figures.py`

**Step 1: Write the test**

Create temporary DML, DML-input, CATE, and policy seed CSV inputs. Run `src/25_export_result_figures.py` with explicit paths and a temporary output directory.

**Step 2: Expected initial result**

Before implementation, the test fails because `src/25_export_result_figures.py` does not exist.

### Task 2: Implement figure exporter

**Files:**
- Create: `src/25_export_result_figures.py`

**Step 1: Add CLI**

Accept explicit paths for:

- DML table;
- DML input table;
- CATE table;
- policy mechanism seed panel;
- output directory;
- manifest path.

**Step 2: Add plotting functions**

Generate:

- `figure_01_digital_finance_carbon_intensity_trends.pdf`;
- `figure_02_dml_effect_intervals.pdf`;
- `figure_03_candidate_cate_distribution.pdf`;
- `figure_04_policy_seed_mechanism_trends.pdf`;
- `figure_manifest.csv`.

**Step 3: Keep caveats explicit**

The manifest should mark the CATE and policy seed figures as candidate/non-final.

### Task 3: Update paper-facing docs

**Files:**
- Modify: `docs/paper/01_draft.md`
- Create: `docs/paper/table-figure-inventory.md`
- Modify: `README.md`

**Step 1: Results skeleton**

Add a results-chapter skeleton covering:

- descriptive visual evidence;
- DML baseline;
- robustness;
- candidate heterogeneity;
- seed policy mechanism.

**Step 2: Table/figure inventory**

List current tables and newly generated figures with status and caveats.

**Step 3: README run order**

Add the reporting script after the current Table 5 export step.

### Task 4: Verify

Run:

```bash
python3 src/25_export_result_figures.py
python3 -m pytest -q
python3 -m py_compile $(find src tests -name '*.py' | sort)
git status --short --branch
```

Expected:

- figures and manifest generated locally;
- all tests pass;
- Python files compile;
- only intended tracked files are staged/committed.
