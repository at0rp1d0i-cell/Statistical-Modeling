# OLS TWFE Robustness Implementation Plan

<execution_handoff>
  <executor>codex</executor>
  <primary_mode>subagent-driven-development</primary_mode>
  <alternate_mode>executing-plans</alternate_mode>
  <rule>Execute task-by-task with verification after each task.</rule>
</execution_handoff>

**Goal:** Add a reproducible candidate OLS two-way fixed effects comparison table for the current DML candidate sample.

**Architecture:** Reuse the planned `src/06_robustness.py` entrypoint rather than adding a new numbered script. The script will read the current DML candidate input, estimate OLS with city and year fixed effects plus the current main-spec controls, cluster standard errors by city, and write ignored paper-ready CSV/LaTeX outputs under `outputs/tables/`.

**Tech Stack:** Python, pandas, statsmodels formula OLS, pytest, existing `stat_modeling.config` paths. No new dependency is introduced because `linearmodels` is unavailable in the current runtime and `statsmodels==0.14.6` is already installed.

---

### Task 1: Add robustness smoke test

**Files:**
- Create: `tests/test_robustness_ols_twfe.py`

**Step 1: Write the failing test**

Create a synthetic city-year panel with outcome, treatment, controls, city IDs, and years. Run `python3 src/06_robustness.py` with explicit paths. Assert that the CSV and TeX outputs are created and include rows for both carbon-intensity and carbon-total style outcomes.

**Step 2: Verify red**

Run:

```bash
python3 -m pytest tests/test_robustness_ols_twfe.py -q
```

Expected before implementation: failure because `src/06_robustness.py` is still a scaffold and writes no outputs.

### Task 2: Implement OLS TWFE candidate exporter

**Files:**
- Modify: `src/06_robustness.py`

**Step 1: Add CLI**

Support:

- `--input-path`
- `--output-csv-path`
- `--output-tex-path`
- `--treatment-column`
- `--outcome-columns`
- `--control-columns`
- `--entity-column`
- `--time-column`
- `--cluster-column`

**Step 2: Fit candidate TWFE models**

For each outcome, estimate:

```text
outcome ~ treatment + controls + C(entity) + C(time)
```

Use city-clustered standard errors. Export the treatment coefficient, standard error, confidence interval, p-value, sample size, fixed-effect flags, and caveat.

**Step 3: Export CSV and LaTeX**

Write:

- `outputs/tables/table_06_ols_twfe_candidate.csv`
- `outputs/tables/table_06_ols_twfe_candidate.tex`

### Task 3: Update docs

**Files:**
- Modify: `README.md`
- Modify: `docs/paper/table-figure-inventory.md`
- Modify: `docs/paper/01_draft.md`
- Modify: `docs/paper/02_manuscript_v0_1.md`
- Modify: `docs/paper/decision-log.md`

Record Table 6 as a candidate robustness comparison and explicitly state it is not a replacement for DML.

### Task 4: Verify and commit

Run:

```bash
python3 src/06_robustness.py
python3 -m pytest -q
python3 -m py_compile $(find src tests -name '*.py' | sort)
git status --short --branch
```

Expected:

- Table 6 CSV and TeX are generated locally under ignored `outputs/tables/`.
- Full tests pass.
- Python files compile.
- Only intended tracked files are committed.
