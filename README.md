# Statistical Modeling Competition Project

## Overview

This repository contains the implementation workflow for the 2026 statistical modeling competition topic:

"Carbon reduction effect of digital inclusive finance under the dual-carbon strategy: causal inference and policy-text mechanism analysis based on double machine learning with Chinese prefecture-level city panel data."

Current Chinese working title: “双碳”战略下数字普惠金融的碳减排效应：基于中国地级市面板的双重机器学习因果推断与政策文本机制分析.

The project uses a `B-lite` structure:

- Numbered scripts under `src/` map to research steps.
- Reusable logic lives in `src/stat_modeling/`.
- Policy-text features remain an auxiliary mechanism/moderation lane; they do not replace the main identification design.

## Setup

Create the conda environment:

```bash
conda env create -f environment.yml
conda activate stat-modeling
```

## Reproducibility

- Global random seed: `RANDOM_SEED = 42`
- Required directories are managed by `stat_modeling.config.ensure_project_directories()`
- Policy-text artifacts are stored under `data/interim/policy_text`, `data/processed/policy_text`, and `logs/policy_text`
- Raw HTML pages and downloaded attachments are organized beneath `data/interim/policy_text/raw_html` and `data/interim/policy_text/attachments`

## Policy Text Module

Use the policy-text scaffold when you need reproducible document discovery, normalization, rule extraction, scoring payload preparation, and `city-year` aggregation for the approved double-carbon corpus window.

```bash
python3 src/08_policy_text.py --help
```

## Planned Run Order

1. `src/01_data_clean.py`
2. `src/02_dea_efficiency.py`
3. `src/03_eda.py` (Table 1 descriptive statistics)
4. `src/04_dml_main.py`
5. `src/05_heterogeneity.py`
6. `src/06_robustness.py` (candidate OLS TWFE robustness comparison)
7. `src/07_spatial.py` (optional)
8. `src/08_policy_text.py` (mechanism/moderation support lane)

Current project-specific continuation scripts:

9. `src/09_cmcc_prepare.py`
10. `src/10_build_pku_cmcc_candidate_panel.py`
11. `src/11_extract_core_controls.py`
12. `src/12_build_modeling_candidate_panel.py`
13. `src/13_prepare_dml_candidate_input.py`
14. `src/14_export_table_02.py`
15. `src/15_export_table_03.py`
16. `src/16_export_table_04.py`
17. `src/17_prepare_policy_mechanism_template.py`
18. `src/18_prepare_policy_text_bootstrap.py`
19. `src/19_seed_policy_registry.py`
20. `src/20_score_policy_seeds.py`
21. `src/21_merge_policy_seed_panel.py`
22. `src/22_build_modeling_policy_seed_panel.py`
23. `src/23_mechanism_seed_regression.py`
24. `src/24_export_table_05.py`
25. `src/25_export_result_figures.py`
26. `src/26_export_evidence_synthesis.py`
27. `src/27_export_heterogeneity_groups.py`
28. `src/28_export_population_sensitivity.py`
29. `src/29_export_heterogeneity_group_differences.py`
30. `src/30_prepare_policy_llm_scoring_batch.py`
31. `src/31_validate_policy_llm_scores.py`

## Policy-text corpus lane

Use the policy-text scaffold to prepare the corpus workspace and record the expected pipeline stage:

```bash
python3 src/08_policy_text.py --help
python3 src/08_policy_text.py --stage discover --dry-run
```

Current scaffold behavior:

- creates the policy-text interim / processed / log folders when missing
- writes a UTF-8 summary under `logs/policy_text/`
- keeps the policy-text module scoped to mechanism and moderation analysis rather than the headline treatment effect

Planned policy-text stages:

- `discover` — identify candidate policy documents on approved official sites
- `normalize` — standardize metadata and text capture
- `rules` — extract rule-based indicators such as deadlines or quantitative targets
- `score` — attach validated LLM scoring outputs
- `aggregate` — roll document scores into city-year features
- `full` — run the full staged pipeline once the package implementation is in place

Current policy-text validation scaffolding can be regenerated with:

```bash
python3 src/30_prepare_policy_llm_scoring_batch.py
python3 src/31_validate_policy_llm_scores.py
```

These commands prepare JSONL scoring payloads, a human/LLM review template, validation detail rows, and `Table 13` readiness output. They do not fabricate LLM scores; a `not_ready` status means the policy-text lane remains technical scaffolding rather than final mechanism evidence.

## Current DML status

The repository now includes a first-pass runnable DML main-regression workflow and a synchronized `Table 2` result export.

Current first-pass mainline:

- sample: `294` cities / `1456` city-year observations
- treatment: `digital_inclusive_finance_index`
- outcome: `co2_emission_intensity`
- controls: `gdp_total`, `secondary_industry_share`, `fiscal_expenditure`
- cross-fitting: `GroupKFold(pku_city_code)`
- covariance: `cluster(pku_city_code)`

Current first-pass robustness result uses `co2_emission_total` as the outcome under the same control set. The population candidate variable is not part of the main regression and is reserved for robustness/sensitivity checks.

## Reporting assets

The current paper-writing entrypoints are:

- `docs/paper/01_draft.md` — project state, writing boundaries, and result notes
- `docs/paper/02_manuscript_v0_1.md` — continuous v0.1 manuscript draft for expansion
- `docs/paper/table-figure-inventory.md` — table, figure, and manuscript asset inventory

Current sample descriptive, robustness, evidence-synthesis, and heterogeneity tables can be regenerated with:

```bash
python3 src/03_eda.py
python3 src/06_robustness.py
python3 src/28_export_population_sensitivity.py
python3 src/27_export_heterogeneity_groups.py
python3 src/29_export_heterogeneity_group_differences.py
python3 src/30_prepare_policy_llm_scoring_batch.py
python3 src/31_validate_policy_llm_scores.py
python3 src/26_export_evidence_synthesis.py
```

First-pass figure assets can be regenerated with:

```bash
python3 src/25_export_result_figures.py
python3 src/27_export_heterogeneity_groups.py
```

These commands write paper-facing tables under `outputs/tables/` and PDF figures plus a manifest under `outputs/figures/`. `src/06_robustness.py` currently exports the OLS TWFE candidate benchmark, the DML residual-permutation placebo check, and the DML learner-replacement robustness table. `src/26_export_evidence_synthesis.py` exports the current evidence-chain synthesis table for writing and presentation. `src/27_export_heterogeneity_groups.py` exports Table 10 and Figure 6 for the confirmed region / economic-development / industrial-structure heterogeneity dimensions. `src/28_export_population_sensitivity.py` exports Table 11 for the population-control sensitivity check. `src/29_export_heterogeneity_group_differences.py` exports Table 12 for city-level bootstrap group-difference diagnostics. `src/31_validate_policy_llm_scores.py` exports Table 13 for policy-text LLM validation readiness. The paper-facing inventory is tracked in `docs/paper/table-figure-inventory.md`. Generated outputs remain ignored by git unless explicitly force-added as final competition artifacts.

## Heterogeneity runtime note

The heterogeneity input-preparation path is runnable in the main environment, but full `econml + shap` CATE / SHAP execution currently depends on a compatible Python environment.

The compatible local runtime currently used in-session is a repo-local virtual environment:

```bash
python3 -m venv .omx/venvs/heterogeneity
./.omx/venvs/heterogeneity/bin/python -m pip install --upgrade pip
./.omx/venvs/heterogeneity/bin/python -m pip install econml==0.15.1 shap==0.43.0 doubleml==0.8.1
PYTHONPATH=src ./.omx/venvs/heterogeneity/bin/python src/05_heterogeneity.py --check-deps
```

Note:

- `econml==0.15.1` is compatible with `shap<0.44`
- therefore `shap==0.43.0` is pinned in `environment.yml`
