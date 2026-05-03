from pathlib import Path
from subprocess import run

import pandas as pd


def test_eda_exports_table_01_with_explicit_paths(tmp_path):
    input_path = tmp_path / "dml_candidate_input.csv"
    output_csv = tmp_path / "table_01.csv"
    output_tex = tmp_path / "table_01.tex"
    pd.DataFrame(
        {
            "co2_emission_intensity": [1.0, 2.0, 3.0],
            "co2_emission_total": [10.0, 20.0, 30.0],
            "digital_inclusive_finance_index": [100.0, 110.0, 120.0],
            "dfi_coverage_breadth": [90.0, 100.0, 110.0],
            "dfi_usage_depth": [80.0, 85.0, 90.0],
            "dfi_digitization_level": [70.0, 75.0, 80.0],
            "gdp_total": [1000.0, 1200.0, 1400.0],
            "secondary_industry_share": [30.0, 35.0, 40.0],
            "fiscal_expenditure": [500.0, 600.0, 700.0],
            "population_control_candidate": [50.0, 55.0, 60.0],
        }
    ).to_csv(input_path, index=False)

    result = run(
        [
            "python3",
            "src/03_eda.py",
            "--input-path",
            str(input_path),
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
    assert "碳排放强度" in exported["变量"].tolist()
    assert "数字普惠金融指数" in exported["变量"].tolist()
    assert "人口规模（候选控制）" in exported["变量"].tolist()
    assert exported.loc[exported["变量"] == "碳排放强度", "样本量"].iloc[0] == 3
