from pathlib import Path
from subprocess import run

import pandas as pd


def test_robustness_exports_ols_twfe_candidate_table(tmp_path):
    input_path = tmp_path / "dml_candidate_input.csv"
    output_csv = tmp_path / "table_06.csv"
    output_tex = tmp_path / "table_06.tex"
    placebo_summary_csv = tmp_path / "table_07_summary.csv"
    placebo_summary_tex = tmp_path / "table_07_summary.tex"
    placebo_distribution_csv = tmp_path / "table_07_distribution.csv"
    placebo_figure = tmp_path / "figure_05.pdf"
    learner_csv = tmp_path / "table_08.csv"
    learner_tex = tmp_path / "table_08.tex"

    rows = []
    for city_id, city_effect in [(1101, 0.2), (1202, -0.1), (1303, 0.05), (1404, -0.05), (1505, 0.1), (1606, -0.2)]:
        for year in [2019, 2020, 2021, 2022]:
            treatment = 10 + (city_id % 100) * 0.01 + (year - 2019)
            gdp = 100 + (city_id % 100) + 2 * (year - 2019)
            industry = 30 + (city_id % 10) + 0.5 * (year - 2019)
            fiscal = 500 + (city_id % 100) * 2 + 3 * (year - 2019)
            rows.append(
                {
                    "pku_city_code": city_id,
                    "year": year,
                    "digital_inclusive_finance_index": treatment,
                    "co2_emission_intensity": 5 - 0.2 * treatment + 0.01 * gdp + city_effect,
                    "co2_emission_total": 200 - 2.0 * treatment + 0.5 * gdp + city_effect * 10,
                    "gdp_total": gdp,
                    "secondary_industry_share": industry,
                    "fiscal_expenditure": fiscal,
                }
            )
    pd.DataFrame(rows).to_csv(input_path, index=False)

    result = run(
        [
            "python3",
            "src/06_robustness.py",
            "--input-path",
            str(input_path),
            "--output-csv-path",
            str(output_csv),
            "--output-tex-path",
            str(output_tex),
            "--placebo-summary-csv-path",
            str(placebo_summary_csv),
            "--placebo-summary-tex-path",
            str(placebo_summary_tex),
            "--placebo-distribution-csv-path",
            str(placebo_distribution_csv),
            "--placebo-figure-path",
            str(placebo_figure),
            "--learner-csv-path",
            str(learner_csv),
            "--learner-tex-path",
            str(learner_tex),
            "--placebo-permutations",
            "20",
            "--folds",
            "3",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output_csv.exists()
    assert output_tex.exists()
    exported = pd.read_csv(output_csv)
    assert set(exported["outcome_column"]) == {"co2_emission_intensity", "co2_emission_total"}
    assert set(exported["model"]) == {"OLS_TWFE_candidate"}
    assert exported["city_fixed_effects"].all()
    assert exported["year_fixed_effects"].all()
    assert placebo_summary_csv.exists()
    assert placebo_summary_tex.exists()
    assert placebo_distribution_csv.exists()
    assert placebo_figure.exists()
    assert placebo_figure.with_suffix(".png").exists()
    assert placebo_figure.with_suffix(".jpg").exists()
    placebo_summary = pd.read_csv(placebo_summary_csv)
    placebo_distribution = pd.read_csv(placebo_distribution_csv)
    assert placebo_summary["permutations"].iloc[0] == 20
    assert len(placebo_distribution) == 20
    assert "empirical_p_value" in placebo_summary.columns
    assert learner_csv.exists()
    assert learner_tex.exists()
    learners = pd.read_csv(learner_csv)
    assert set(learners["learner_label"]) == {
        "GradientBoosting baseline",
        "RandomForest replacement",
        "ExtraTrees replacement",
    }
    assert set(learners["model"]) == {"DML_learner_replacement_candidate"}
