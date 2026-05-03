from pathlib import Path
from subprocess import run

import numpy as np
import pandas as pd


def test_export_population_sensitivity_runs_with_explicit_inputs(tmp_path):
    input_path = tmp_path / "dml_input.csv"
    output_csv = tmp_path / "table_11.csv"
    output_tex = tmp_path / "table_11.tex"
    rng = np.random.default_rng(42)
    rows = []
    for city_idx in range(12):
        city_code = 1100 + city_idx
        city_effect = rng.normal(scale=0.2)
        for year in [2019, 2020, 2021, 2022, 2023]:
            x1 = rng.normal()
            x2 = rng.normal()
            pop = 200 + 10 * city_idx + rng.normal(scale=5)
            treatment = 100 + 0.5 * x1 - 0.2 * x2 + 0.01 * pop + rng.normal(scale=0.2)
            outcome = 10 - 0.08 * treatment + 0.4 * x1 + 0.2 * x2 + 0.005 * pop + city_effect
            rows.append(
                {
                    "year": year,
                    "pku_city_code": city_code,
                    "digital_inclusive_finance_index": treatment,
                    "co2_emission_intensity": outcome,
                    "gdp_total": x1,
                    "secondary_industry_share": x2,
                    "fiscal_expenditure": x1 + x2,
                    "population_control_candidate": pop,
                }
            )
    pd.DataFrame(rows).to_csv(input_path, index=False)

    result = run(
        [
            "python3",
            "src/28_export_population_sensitivity.py",
            "--input-path",
            str(input_path),
            "--output-csv-path",
            str(output_csv),
            "--output-tex-path",
            str(output_tex),
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
    assert exported["spec_key"].tolist() == ["baseline_no_population", "population_augmented"]
    assert exported["population_included"].tolist() == [False, True]
    assert "ate_delta_vs_baseline" in exported.columns
