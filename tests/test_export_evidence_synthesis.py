from pathlib import Path
from subprocess import run

import pandas as pd


def test_export_evidence_synthesis_runs_with_explicit_inputs(tmp_path):
    dml_table = tmp_path / "table_02.csv"
    twfe_table = tmp_path / "table_06.csv"
    placebo_table = tmp_path / "table_07.csv"
    learner_table = tmp_path / "table_08.csv"
    cate_summary = tmp_path / "cate_summary.csv"
    policy_table = tmp_path / "table_05.csv"
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
            "nobs": [100],
            "cate_mean": [-0.05],
            "cate_median": [-0.03],
        }
    ).to_csv(cate_summary, index=False)
    pd.DataFrame(
        {
            "variable_name": ["policy_strength"],
            "coefficient": [1.0],
            "p_value": [0.01],
            "nobs": [100],
        }
    ).to_csv(policy_table, index=False)

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
            "--cate-summary-path",
            str(cate_summary),
            "--policy-table-path",
            str(policy_table),
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
    assert len(exported) == 8
    assert "DML主结果" in exported["证据环节"].tolist()
    assert "政策文本机制" in exported["证据环节"].tolist()
    assert exported.loc[exported["证据环节"] == "政策文本机制", "论文用途"].iloc[0] == "技术附录"
