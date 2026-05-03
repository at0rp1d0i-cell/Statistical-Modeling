# Table 01 Descriptive Statistics Implementation Plan

<execution_handoff>
  <executor>codex</executor>
  <primary_mode>subagent-driven-development</primary_mode>
  <alternate_mode>executing-plans</alternate_mode>
  <rule>Execute task-by-task with verification after each task.</rule>
</execution_handoff>

**Goal:** Add a reproducible Table 1 descriptive-statistics export for the current 2019—2023 city-year candidate DML sample.

**Architecture:** Reuse the existing `src/03_eda.py` placeholder as the descriptive-statistics entrypoint instead of adding another numbered reporting script. The script reads the current candidate DML input, summarizes pre-declared paper variables, and writes ignored CSV/LaTeX assets under `outputs/tables/`.

**Tech Stack:** Python, pandas, argparse, pytest, existing `stat_modeling.config` paths.

---

### Task 1: Add smoke coverage for Table 1 export

**Files:**
- Modify: `tests/test_data_clean_pipeline_smoke.py` is not appropriate; create a targeted test instead.
- Create: `tests/test_eda_table_01.py`

**Step 1: Write the failing test**

Create a temporary CSV with the Table 1 source columns. Run `python3 src/03_eda.py` with explicit input/output paths. Assert that the CSV and TeX files are created and that the output contains labeled rows for the main outcome, treatment, controls, and candidate population variable.

**Step 2: Verify red**

Run:

```bash
python3 -m pytest tests/test_eda_table_01.py -q
```

Expected before implementation: failure because `src/03_eda.py` has no CLI and does not write outputs.

### Task 2: Implement `src/03_eda.py`

**Files:**
- Modify: `src/03_eda.py`

**Step 1: Add CLI**

Support:

- `--input-path`
- `--output-csv-path`
- `--output-tex-path`

**Step 2: Add fixed variable registry**

Summarize the current candidate paper variables:

- `co2_emission_intensity`
- `co2_emission_total`
- `digital_inclusive_finance_index`
- `dfi_coverage_breadth`
- `dfi_usage_depth`
- `dfi_digitization_level`
- `gdp_total`
- `secondary_industry_share`
- `fiscal_expenditure`
- `population_control_candidate`

Label `population_control_candidate` as a candidate control so the script does not lock it into the main specification.

**Step 3: Export CSV and LaTeX**

Write:

- `outputs/tables/table_01_descriptive_statistics.csv`
- `outputs/tables/table_01_descriptive_statistics.tex`

### Task 3: Update paper-facing docs

**Files:**
- Modify: `README.md`
- Modify: `docs/paper/table-figure-inventory.md`
- Modify: `docs/paper/01_draft.md`
- Modify: `docs/paper/decision-log.md`

**Step 1: Document the script**

Record that `src/03_eda.py` now generates Table 1 from the current candidate sample.

**Step 2: Preserve caveats**

Keep the sample and population-control caveats explicit: this is a current candidate-sample descriptive table, not a final sample/specification lock.

### Task 4: Verify and commit

Run:

```bash
python3 src/03_eda.py
python3 -m pytest -q
python3 -m py_compile $(find src tests -name '*.py' | sort)
git status --short --branch
```

Expected:

- Table 1 CSV and TeX are generated locally under ignored `outputs/tables/`.
- Full test suite passes.
- Python files compile.
- Only intended tracked files are committed.
