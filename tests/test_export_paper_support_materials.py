from pathlib import Path
from subprocess import run

import pandas as pd


def test_export_paper_support_materials_runs_with_explicit_inputs(tmp_path):
    modeling_panel = tmp_path / "modeling_panel.csv"
    dml_input = tmp_path / "dml_input.csv"
    cate_groups = tmp_path / "cate_groups.csv"
    table_02 = tmp_path / "table_02.csv"
    table_06 = tmp_path / "table_06.csv"
    table_08 = tmp_path / "table_08.csv"
    table_11 = tmp_path / "table_11.csv"
    tables_dir = tmp_path / "tables"
    figures_dir = tmp_path / "figures"

    pd.DataFrame(
        {
            "year": [2019, 2020, 2021, 2022],
            "pku_city_code": [1, 1, 2, 2],
            "has_cmcc_outcome": [True, True, True, False],
            "has_core_controls": [True, True, False, True],
            "ready_for_dml_candidate": [True, True, False, False],
        }
    ).to_csv(modeling_panel, index=False)
    pd.DataFrame(
        {
            "year": [2019, 2020, 2019, 2020],
            "pku_city_code": [1, 1, 2, 2],
            "digital_inclusive_finance_index": [100.0, 105.0, 80.0, 90.0],
            "dfi_coverage_breadth": [90.0, 95.0, 70.0, 75.0],
            "dfi_usage_depth": [85.0, 88.0, 60.0, 65.0],
            "dfi_digitization_level": [95.0, 98.0, 75.0, 80.0],
            "co2_emission_total": [1000.0, 990.0, 1200.0, 1180.0],
            "co2_emission_intensity": [10.0, 9.5, 12.0, 11.4],
            "gdp_total": [100.0, 104.0, 100.0, 103.0],
            "secondary_industry_share": [40.0, 39.0, 45.0, 44.0],
            "fiscal_expenditure": [20.0, 22.0, 15.0, 16.0],
            "population_control_candidate": [50.0, 51.0, 60.0, 61.0],
        }
    ).to_csv(dml_input, index=False)
    pd.DataFrame({"pku_city_code": [1, 2], "region_group_cn": ["东部", "西部"]}).to_csv(cate_groups, index=False)
    pd.DataFrame(
        {
            "outcome_column": ["co2_emission_intensity", "co2_emission_total"],
            "ate": [-0.05, -100.0],
            "ci_lower": [-0.08, -200.0],
            "ci_upper": [-0.02, -10.0],
            "p_value": [0.01, 0.02],
        }
    ).to_csv(table_02, index=False)
    pd.DataFrame(
        {
            "outcome_column": ["co2_emission_intensity"],
            "coefficient": [-0.06],
            "ci_lower": [-0.09],
            "ci_upper": [-0.03],
            "p_value": [0.005],
        }
    ).to_csv(table_06, index=False)
    pd.DataFrame(
        {
            "learner_label": ["GradientBoosting baseline", "RandomForest replacement"],
            "ate": [-0.05, -0.04],
            "ci_lower": [-0.08, -0.07],
            "ci_upper": [-0.02, -0.01],
            "p_value": [0.01, 0.04],
        }
    ).to_csv(table_08, index=False)
    pd.DataFrame(
        {
            "spec_key": ["population_augmented"],
            "ate": [-0.02],
            "ci_lower": [-0.06],
            "ci_upper": [0.02],
            "p_value": [0.4],
        }
    ).to_csv(table_11, index=False)

    result = run(
        [
            "python3",
            "src/34_export_paper_support_materials.py",
            "--modeling-panel-path",
            str(modeling_panel),
            "--dml-input-path",
            str(dml_input),
            "--cate-groups-path",
            str(cate_groups),
            "--table-02-path",
            str(table_02),
            "--table-06-path",
            str(table_06),
            "--table-08-path",
            str(table_08),
            "--table-11-path",
            str(table_11),
            "--tables-dir",
            str(tables_dir),
            "--figures-dir",
            str(figures_dir),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (tables_dir / "table_14_sample_construction_coverage.csv").exists()
    assert (tables_dir / "table_15_variable_correlation_matrix.csv").exists()
    for stem in [
        "figure_07_sample_coverage_by_year",
        "figure_08_robustness_evidence_forest",
        "figure_09_regional_descriptive_trends",
        "figure_10_research_framework",
    ]:
        assert (figures_dir / f"{stem}.pdf").exists()
        assert (figures_dir / f"{stem}.png").exists()
        assert (figures_dir / f"{stem}.jpg").exists()

    sample_table = pd.read_csv(tables_dir / "table_14_sample_construction_coverage.csv")
    assert "最终 DML 输入样本" in sample_table["stage_cn"].tolist()
    correlation_table = pd.read_csv(tables_dir / "table_15_variable_correlation_matrix.csv")
    assert "数字普惠金融" in correlation_table.columns
