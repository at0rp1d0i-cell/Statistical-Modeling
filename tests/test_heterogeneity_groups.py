from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stat_modeling.modeling.heterogeneity_groups import build_city_group_attributes
from stat_modeling.modeling.heterogeneity_groups import build_heterogeneity_group_summary
from stat_modeling.modeling.heterogeneity_groups import build_pairwise_group_differences
from stat_modeling.modeling.heterogeneity_groups import region_info_for_city_code


def test_region_mapping_uses_standard_four_region_groups():
    assert region_info_for_city_code(1100)[:2] == ("east", "东部")
    assert region_info_for_city_code(4201)[:2] == ("central", "中部")
    assert region_info_for_city_code(5101)[:2] == ("west", "西部")
    assert region_info_for_city_code(2101)[:2] == ("northeast", "东北")


def test_build_city_group_attributes_adds_region_and_median_splits():
    model = pd.DataFrame(
        {
            "pku_city_code": [1100, 1100, 4201, 4201, 5101, 5101, 2101, 2101],
            "pku_city_name_cn": ["北京", "北京", "武汉", "武汉", "成都", "成都", "沈阳", "沈阳"],
            "gdp_total": [100, 120, 80, 90, 50, 55, 70, 75],
            "secondary_industry_share": [20, 22, 45, 46, 35, 36, 30, 31],
        }
    )
    result = build_city_group_attributes(model)
    assert set(result["region_group_cn"]) == {"东部", "中部", "西部", "东北"}
    assert set(result["economic_development_group_cn"]) == {"高经济发展水平", "低经济发展水平"}
    assert set(result["industrial_structure_group_cn"]) == {"高第二产业占比", "低第二产业占比"}


def test_build_heterogeneity_group_summary_counts_observations_and_cities():
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

    summary, attached = build_heterogeneity_group_summary(cate, model)

    assert len(summary) == 8
    assert len(attached) == len(cate)
    region_rows = summary.loc[summary["dimension_key"] == "region"]
    assert set(region_rows["group_cn"]) == {"东部", "中部", "西部", "东北"}
    assert region_rows["n_obs"].sum() == len(cate)
    assert region_rows["n_city"].sum() == cate["pku_city_code"].nunique()
    assert "result_boundary" in summary.columns


def test_build_pairwise_group_differences_uses_city_level_cate():
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
    _, attached = build_heterogeneity_group_summary(cate, model)

    differences = build_pairwise_group_differences(attached, n_bootstrap=50, random_seed=42)

    assert set(differences["dimension_cn"]) == {"区域", "经济发展水平", "产业结构"}
    assert "mean_difference_a_minus_b" in differences.columns
    assert "p_value_approx" in differences.columns
    econ = differences.loc[differences["dimension_key"] == "economic_development"].iloc[0]
    assert econ["group_a_cn"] == "高经济发展水平"
    assert econ["group_b_cn"] == "低经济发展水平"
