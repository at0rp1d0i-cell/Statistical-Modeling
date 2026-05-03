from pathlib import Path
from subprocess import run

import pandas as pd


def test_export_result_figures_runs_with_explicit_inputs(tmp_path):
    dml_table = tmp_path / "dml_table.csv"
    dml_input = tmp_path / "dml_input.csv"
    cate_input = tmp_path / "cate.csv"
    policy_panel = tmp_path / "policy.csv"
    figure_dir = tmp_path / "figures"
    manifest = figure_dir / "manifest.csv"

    pd.DataFrame(
        {
            "ate": [-0.05, -120.0],
            "std_error": [0.01, 40.0],
            "ci_lower": [-0.07, -200.0],
            "ci_upper": [-0.03, -40.0],
            "p_value": [0.01, 0.02],
            "nobs": [100, 100],
            "outcome_label_en": ["Carbon Intensity", "Carbon Total"],
        }
    ).to_csv(dml_table, index=False)
    pd.DataFrame(
        {
            "year": [2019, 2020, 2021, 2019, 2020, 2021],
            "digital_inclusive_finance_index": [100, 110, 120, 90, 100, 110],
            "co2_emission_intensity": [5.0, 4.8, 4.6, 6.0, 5.8, 5.6],
        }
    ).to_csv(dml_input, index=False)
    pd.DataFrame({"cate_hat": [-0.1, -0.05, 0.0, 0.02]}).to_csv(cate_input, index=False)
    pd.DataFrame(
        {
            "year": [2019, 2020, 2021],
            "sum_policy_strength_city_year": [1.0, 2.0, 3.0],
            "mean_execution_clarity_city_year": [0.5, 0.6, 0.7],
            "mean_digital_green_synergy_city_year": [0.2, 0.3, 0.4],
        }
    ).to_csv(policy_panel, index=False)

    result = run(
        [
            "python3",
            "src/25_export_result_figures.py",
            "--dml-table-path",
            str(dml_table),
            "--dml-input-path",
            str(dml_input),
            "--cate-path",
            str(cate_input),
            "--policy-panel-path",
            str(policy_panel),
            "--output-dir",
            str(figure_dir),
            "--manifest-path",
            str(manifest),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    expected = {
        "figure_01_digital_finance_carbon_intensity_trends.pdf",
        "figure_01_digital_finance_carbon_intensity_trends.png",
        "figure_01_digital_finance_carbon_intensity_trends.jpg",
        "figure_02_dml_effect_intervals.pdf",
        "figure_02_dml_effect_intervals.png",
        "figure_02_dml_effect_intervals.jpg",
        "figure_03_candidate_cate_distribution.pdf",
        "figure_03_candidate_cate_distribution.png",
        "figure_03_candidate_cate_distribution.jpg",
        "figure_04_policy_seed_mechanism_snapshot.pdf",
        "figure_04_policy_seed_mechanism_snapshot.png",
        "figure_04_policy_seed_mechanism_snapshot.jpg",
            "manifest.csv",
        }
    assert expected.issubset({path.name for path in figure_dir.iterdir()})
    exported_manifest = pd.read_csv(manifest)
    figure_04 = exported_manifest.loc[exported_manifest["figure_id"] == "Figure 4"].iloc[0]
    assert figure_04["filename"] == "figure_04_policy_seed_mechanism_snapshot.pdf"
    assert figure_04["png_filename"] == "figure_04_policy_seed_mechanism_snapshot.png"
    assert figure_04["jpg_filename"] == "figure_04_policy_seed_mechanism_snapshot.jpg"
    assert "not a validated LLM trend" in figure_04["caveat"]
