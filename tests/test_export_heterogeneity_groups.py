from pathlib import Path
from subprocess import run

import pandas as pd


def test_export_heterogeneity_groups_runs_with_explicit_inputs(tmp_path):
    cate_path = tmp_path / "cate.csv"
    model_path = tmp_path / "model.csv"
    output_csv = tmp_path / "table_10.csv"
    output_tex = tmp_path / "table_10.tex"
    attached_csv = tmp_path / "attached.csv"
    figure_path = tmp_path / "figure_06.pdf"

    model = pd.DataFrame(
        {
            "year": [2020, 2021, 2020, 2021, 2020, 2021, 2020, 2021],
            "pku_city_code": [1100, 1100, 4201, 4201, 5101, 5101, 2101, 2101],
            "pku_city_name_cn": ["北京", "北京", "武汉", "武汉", "成都", "成都", "沈阳", "沈阳"],
            "gdp_total": [100, 120, 80, 90, 50, 55, 70, 75],
            "secondary_industry_share": [20, 22, 45, 46, 35, 36, 30, 31],
        }
    )
    cate = model[["year", "pku_city_code", "pku_city_name_cn"]].copy()
    cate["pku_city_name_eng"] = ["A", "A", "B", "B", "C", "C", "D", "D"]
    cate["cate_hat"] = [-0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8]
    cate["cate_ci_lower"] = cate["cate_hat"] - 0.1
    cate["cate_ci_upper"] = cate["cate_hat"] + 0.1
    model.to_csv(model_path, index=False)
    cate.to_csv(cate_path, index=False)

    result = run(
        [
            "python3",
            "src/27_export_heterogeneity_groups.py",
            "--cate-path",
            str(cate_path),
            "--model-input-path",
            str(model_path),
            "--output-csv-path",
            str(output_csv),
            "--output-tex-path",
            str(output_tex),
            "--attached-csv-path",
            str(attached_csv),
            "--figure-path",
            str(figure_path),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output_csv.exists()
    assert output_tex.exists()
    assert attached_csv.exists()
    assert figure_path.exists()
    assert figure_path.with_suffix(".png").exists()
    assert figure_path.with_suffix(".jpg").exists()
    exported = pd.read_csv(output_csv)
    assert len(exported) == 8
    assert set(exported["dimension_cn"]) == {"区域", "经济发展水平", "产业结构"}
