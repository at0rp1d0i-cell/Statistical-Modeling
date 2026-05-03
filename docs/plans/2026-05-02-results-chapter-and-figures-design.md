# Results Chapter and Figure Assets Design

## Goal

Build a reproducible bridge from the current modeling outputs to the paper draft: a results-section skeleton, a table/figure inventory, and a script that regenerates first-pass figures from existing interim tables.

## Current context

- The DML main result and total-emissions robustness result are already exported in `outputs/tables/table_02_dml_main_and_robustness.csv`.
- Candidate CATE outputs are already available in `data/interim/modeling/heterogeneity_candidate_cate.csv`.
- Seed policy-text mechanism outputs are already available in `data/interim/policy_text/policy_mechanism_seed_panel_2019_2023.csv` and `outputs/tables/table_05_policy_seed_mechanism_candidate.csv`.
- `outputs/*` and `data/interim/*` are ignored by git, so source scripts and paper-facing documentation are the stable versioned contract.

## Approaches considered

### Approach A: Write only prose

Fastest, but weak for reproducibility. It would leave the paper draft detached from generated assets.

### Approach B: Add one small figure-export script plus a paper inventory

Recommended. This creates a concrete result-to-paper handoff without changing research design. The script can generate first-pass figures from current outputs, while the inventory clearly labels provisional and non-final assets.

### Approach C: Build a full reporting package now

More scalable, but too heavy before the final sample, policy corpus, and headline heterogeneity dimensions are locked.

## Chosen design

Use Approach B.

Add `src/25_export_result_figures.py` as a thin numbered reporting entrypoint. It will read the current DML, DML-input, CATE, and seed policy mechanism tables and emit four PDF figures plus a figure manifest:

1. normalized annual trend for digital inclusive finance and carbon intensity;
2. DML estimate intervals for the main and robustness outcomes;
3. candidate CATE distribution;
4. seed policy mechanism coverage and score snapshot.

Update `docs/paper/01_draft.md` with a results-chapter skeleton that separates current evidence from non-final research-design claims. Add `docs/paper/table-figure-inventory.md` as the paper-facing checklist for tables and figures.

## Boundaries

- Do not change model specifications.
- Do not promote seed policy mechanism evidence to a final LLM-validated mechanism conclusion.
- Do not decide whether `population_control_candidate` enters the main specification.
- Do not treat candidate heterogeneity features as final headline heterogeneity dimensions.

## Verification

- Unit/smoke test the figure exporter with synthetic temporary inputs.
- Run the script on current project data.
- Run the full pytest suite.
- Run Python compilation over `src/` and `tests/`.
