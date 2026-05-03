from pathlib import Path
from subprocess import run

import pandas as pd


def test_export_heterogeneity_group_differences_runs_with_explicit_inputs(tmp_path):
    cate_with_groups_path = tmp_path / "cate_with_groups.csv"
    output_csv = tmp_path / "table_12.csv"
    output_tex = tmp_path / "table_12.tex"
    frame = pd.DataFrame(
        {
            "year": [2020, 2021, 2020, 2021, 2020, 2021, 2020, 2021],
            "pku_city_code": [1100, 1100, 4201, 4201, 5101, 5101, 2101, 2101],
            "cate_hat": [-0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8],
            "region_group_cn": ["东部", "东部", "中部", "中部", "西部", "西部", "东北", "东北"],
            "region_group_order": [1, 1, 2, 2, 3, 3, 4, 4],
            "economic_development_group_cn": [
                "高经济发展水平",
                "高经济发展水平",
                "高经济发展水平",
                "高经济发展水平",
                "低经济发展水平",
                "低经济发展水平",
                "低经济发展水平",
                "低经济发展水平",
            ],
            "economic_development_group_order": [1, 1, 1, 1, 2, 2, 2, 2],
            "industrial_structure_group_cn": [
                "低第二产业占比",
                "低第二产业占比",
                "高第二产业占比",
                "高第二产业占比",
                "高第二产业占比",
                "高第二产业占比",
                "低第二产业占比",
                "低第二产业占比",
            ],
            "industrial_structure_group_order": [2, 2, 1, 1, 1, 1, 2, 2],
        }
    )
    frame.to_csv(cate_with_groups_path, index=False)

    result = run(
        [
            "python3",
            "src/29_export_heterogeneity_group_differences.py",
            "--cate-with-groups-path",
            str(cate_with_groups_path),
            "--output-csv-path",
            str(output_csv),
            "--output-tex-path",
            str(output_tex),
            "--n-bootstrap",
            "50",
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
    assert set(exported["dimension_cn"]) == {"区域", "经济发展水平", "产业结构"}
    assert "mean_difference_a_minus_b" in exported.columns
    assert "result_boundary" in exported.columns
