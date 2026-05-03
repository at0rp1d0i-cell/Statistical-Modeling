from pathlib import Path
from subprocess import run

import pandas as pd


def test_robustness_exports_ols_twfe_candidate_table(tmp_path):
    input_path = tmp_path / "dml_candidate_input.csv"
    output_csv = tmp_path / "table_06.csv"
    output_tex = tmp_path / "table_06.tex"

    rows = []
    for city_id, city_effect in [(1100, 0.2), (1200, -0.1), (1300, 0.05), (1400, -0.05), (1500, 0.1), (1600, -0.2)]:
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
