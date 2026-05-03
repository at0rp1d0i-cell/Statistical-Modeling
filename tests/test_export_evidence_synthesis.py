from pathlib import Path
from subprocess import run

import pandas as pd


def test_export_evidence_synthesis_runs_with_explicit_inputs(tmp_path):
    dml_table = tmp_path / "table_02.csv"
    twfe_table = tmp_path / "table_06.csv"
    placebo_table = tmp_path / "table_07.csv"
    learner_table = tmp_path / "table_08.csv"
    population_table = tmp_path / "table_11.csv"
    cate_summary = tmp_path / "cate_summary.csv"
    heterogeneity_group_table = tmp_path / "table_10.csv"
    heterogeneity_difference_table = tmp_path / "table_12.csv"
    policy_table = tmp_path / "table_05.csv"
    policy_llm_validation_table = tmp_path / "table_13.csv"
    output_csv = tmp_path / "table_09.csv"
    output_tex = tmp_path / "table_09.tex"

    pd.DataFrame(
        {
            "outcome_column": ["co2_emission_intensity", "co2_emission_total"],
            "ate": [-0.05, -100.0],
            "ci_lower": [-0.08, -150.0],
            "ci_upper": [-0.01, -50.0],
            "p_value": [0.01, 0.02],
        }
    ).to_csv(dml_table, index=False)
    pd.DataFrame(
        {
            "outcome_column": ["co2_emission_intensity", "co2_emission_total"],
            "coefficient": [-0.06, 20.0],
            "ci_lower": [-0.10, -5.0],
            "ci_upper": [-0.02, 45.0],
            "p_value": [0.01, 0.10],
        }
    ).to_csv(twfe_table, index=False)
    pd.DataFrame(
        {
            "true_ate": [-0.05],
            "placebo_mean": [0.0],
            "placebo_q025": [-0.03],
            "placebo_q975": [0.03],
            "empirical_p_value": [0.004],
            "permutations": [500],
        }
    ).to_csv(placebo_table, index=False)
    pd.DataFrame(
        {
            "learner_label": ["A", "B", "C"],
            "ate": [-0.05, -0.04, -0.03],
            "p_value": [0.01, 0.04, 0.05],
        }
    ).to_csv(learner_table, index=False)
    pd.DataFrame(
        {
            "spec_key": ["baseline_no_population", "population_augmented"],
            "ate": [-0.05, -0.02],
            "ci_lower": [-0.08, -0.06],
            "ci_upper": [-0.01, 0.02],
            "p_value": [0.01, 0.40],
            "ate_delta_vs_baseline": [0.0, 0.03],
        }
    ).to_csv(population_table, index=False)
    pd.DataFrame(
        {
            "nobs": [100],
            "cate_mean": [-0.05],
            "cate_median": [-0.03],
        }
    ).to_csv(cate_summary, index=False)
    pd.DataFrame(
        {
            "dimension_cn": ["区域", "区域"],
            "group_cn": ["东部", "西部"],
            "cate_mean": [-0.03, -0.07],
            "n_city": [50, 50],
        }
    ).to_csv(heterogeneity_group_table, index=False)
    pd.DataFrame(
        {
            "dimension_cn": ["区域"],
            "group_a_cn": ["东部"],
            "group_b_cn": ["西部"],
            "mean_difference_a_minus_b": [0.04],
            "p_value_approx": [0.03],
        }
    ).to_csv(heterogeneity_difference_table, index=False)
    pd.DataFrame(
        {
            "variable_name": ["policy_strength"],
            "coefficient": [1.0],
            "p_value": [0.01],
            "nobs": [100],
        }
    ).to_csv(policy_table, index=False)
    pd.DataFrame(
        {
            "readiness_status": ["not_ready"],
            "total_registered_docs": [3],
            "validation_ready_rows": [0],
        }
    ).to_csv(policy_llm_validation_table, index=False)

    result = run(
        [
            "python3",
            "src/26_export_evidence_synthesis.py",
            "--dml-table-path",
            str(dml_table),
            "--twfe-table-path",
            str(twfe_table),
            "--placebo-summary-path",
            str(placebo_table),
            "--learner-table-path",
            str(learner_table),
            "--population-sensitivity-table-path",
            str(population_table),
            "--cate-summary-path",
            str(cate_summary),
            "--heterogeneity-group-table-path",
            str(heterogeneity_group_table),
            "--heterogeneity-difference-table-path",
            str(heterogeneity_difference_table),
            "--policy-table-path",
            str(policy_table),
            "--policy-llm-validation-table-path",
            str(policy_llm_validation_table),
            "--output-csv-path",
            str(output_csv),
            "--output-tex-path",
            str(output_tex),
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
    assert len(exported) == 9
    assert "DML主结果" in exported["证据环节"].tolist()
    assert "政策文本机制" in exported["证据环节"].tolist()
    assert "正式异质性分组" in exported["证据环节"].tolist()
    assert "人口变量敏感性" in exported["证据环节"].tolist()
    assert exported.loc[exported["证据环节"] == "政策文本机制", "论文用途"].iloc[0] == "技术附录"
    assert exported.loc[exported["证据环节"] == "政策文本机制", "来源"].iloc[0] == "Table 5 / Table 13 / Figure 4"
    assert exported.loc[exported["证据环节"] == "正式异质性分组", "来源"].iloc[0] == "Table 10 / Table 12 / Figure 6"
