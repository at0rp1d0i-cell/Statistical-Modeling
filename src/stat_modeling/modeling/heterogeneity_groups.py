from __future__ import annotations

from itertools import combinations
from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Iterable

import numpy as np
import pandas as pd


REGION_BY_PROVINCE_PREFIX: dict[int, tuple[str, str, int]] = {
    # Eastern region: Beijing, Tianjin, Hebei, Shanghai, Jiangsu, Zhejiang,
    # Fujian, Shandong, Guangdong, Hainan.
    11: ("east", "东部", 1),
    12: ("east", "东部", 1),
    13: ("east", "东部", 1),
    31: ("east", "东部", 1),
    32: ("east", "东部", 1),
    33: ("east", "东部", 1),
    35: ("east", "东部", 1),
    37: ("east", "东部", 1),
    44: ("east", "东部", 1),
    46: ("east", "东部", 1),
    # Central region: Shanxi, Anhui, Jiangxi, Henan, Hubei, Hunan.
    14: ("central", "中部", 2),
    34: ("central", "中部", 2),
    36: ("central", "中部", 2),
    41: ("central", "中部", 2),
    42: ("central", "中部", 2),
    43: ("central", "中部", 2),
    # Western region: Inner Mongolia, Guangxi, Chongqing, Sichuan, Guizhou,
    # Yunnan, Tibet, Shaanxi, Gansu, Qinghai, Ningxia, Xinjiang.
    15: ("west", "西部", 3),
    45: ("west", "西部", 3),
    50: ("west", "西部", 3),
    51: ("west", "西部", 3),
    52: ("west", "西部", 3),
    53: ("west", "西部", 3),
    54: ("west", "西部", 3),
    61: ("west", "西部", 3),
    62: ("west", "西部", 3),
    63: ("west", "西部", 3),
    64: ("west", "西部", 3),
    65: ("west", "西部", 3),
    # Northeast region: Liaoning, Jilin, Heilongjiang.
    21: ("northeast", "东北", 4),
    22: ("northeast", "东北", 4),
    23: ("northeast", "东北", 4),
}


@dataclass(frozen=True, slots=True)
class GroupDimension:
    key: str
    label_cn: str
    group_column: str
    order_column: str
    rule: str


GROUP_DIMENSIONS: tuple[GroupDimension, ...] = (
    GroupDimension(
        key="region",
        label_cn="区域",
        group_column="region_group_cn",
        order_column="region_group_order",
        rule="按城市行政区划省级代码映射为东部、中部、西部、东北四大区域。",
    ),
    GroupDimension(
        key="economic_development",
        label_cn="经济发展水平",
        group_column="economic_development_group_cn",
        order_column="economic_development_group_order",
        rule="按城市 2019—2023 年 GDP 均值的样本中位数划分，高于或等于中位数为高组。",
    ),
    GroupDimension(
        key="industrial_structure",
        label_cn="产业结构",
        group_column="industrial_structure_group_cn",
        order_column="industrial_structure_group_order",
        rule="按城市 2019—2023 年第二产业占比均值的样本中位数划分，高于或等于中位数为高组。",
    ),
)


def require_columns(frame: pd.DataFrame, columns: Iterable[str], source_name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{source_name} missing required columns: {missing}")


def province_prefix(city_code: int | float | str) -> int:
    return int(float(city_code)) // 100


def region_info_for_city_code(city_code: int | float | str) -> tuple[str, str, int]:
    prefix = province_prefix(city_code)
    try:
        return REGION_BY_PROVINCE_PREFIX[prefix]
    except KeyError as exc:
        raise ValueError(f"Unsupported province prefix for city code {city_code!r}: {prefix}") from exc


def median_split(values: pd.Series, high_label: str, low_label: str) -> tuple[pd.Series, float]:
    median = float(values.median())
    labels = pd.Series(np.where(values >= median, high_label, low_label), index=values.index)
    return labels, median


def build_city_group_attributes(model_frame: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        model_frame,
        ["pku_city_code", "pku_city_name_cn", "gdp_total", "secondary_industry_share"],
        "model_frame",
    )
    city = (
        model_frame.groupby(["pku_city_code", "pku_city_name_cn"], as_index=False)
        .agg(
            gdp_total_mean=("gdp_total", "mean"),
            secondary_industry_share_mean=("secondary_industry_share", "mean"),
        )
        .sort_values("pku_city_code")
        .reset_index(drop=True)
    )
    region_info = city["pku_city_code"].map(region_info_for_city_code)
    city["region_group_key"] = region_info.map(lambda item: item[0])
    city["region_group_cn"] = region_info.map(lambda item: item[1])
    city["region_group_order"] = region_info.map(lambda item: item[2])

    econ_labels, gdp_median = median_split(city["gdp_total_mean"], "高经济发展水平", "低经济发展水平")
    city["economic_development_group_cn"] = econ_labels
    city["economic_development_group_order"] = np.where(city["gdp_total_mean"] >= gdp_median, 1, 2)
    city["economic_development_cutoff"] = gdp_median

    industry_labels, industry_median = median_split(
        city["secondary_industry_share_mean"],
        "高第二产业占比",
        "低第二产业占比",
    )
    city["industrial_structure_group_cn"] = industry_labels
    city["industrial_structure_group_order"] = np.where(
        city["secondary_industry_share_mean"] >= industry_median,
        1,
        2,
    )
    city["industrial_structure_cutoff"] = industry_median
    return city


def attach_group_attributes(cate_frame: pd.DataFrame, model_frame: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        cate_frame,
        ["year", "pku_city_code", "pku_city_name_cn", "cate_hat", "cate_ci_lower", "cate_ci_upper"],
        "cate_frame",
    )
    city_groups = build_city_group_attributes(model_frame)
    group_columns = [
        "pku_city_code",
        "region_group_key",
        "region_group_cn",
        "region_group_order",
        "gdp_total_mean",
        "economic_development_group_cn",
        "economic_development_group_order",
        "economic_development_cutoff",
        "secondary_industry_share_mean",
        "industrial_structure_group_cn",
        "industrial_structure_group_order",
        "industrial_structure_cutoff",
    ]
    merged = cate_frame.merge(city_groups[group_columns], on="pku_city_code", how="left", validate="many_to_one")
    missing = merged.loc[merged["region_group_cn"].isna(), "pku_city_code"].drop_duplicates().tolist()
    if missing:
        raise ValueError(f"CATE rows without group attributes for city codes: {missing[:10]}")
    return merged


def summarize_grouped_cate(cate_with_groups: pd.DataFrame) -> pd.DataFrame:
    require_columns(cate_with_groups, ["pku_city_code", "cate_hat"], "cate_with_groups")
    rows: list[dict[str, object]] = []
    for dimension in GROUP_DIMENSIONS:
        require_columns(cate_with_groups, [dimension.group_column, dimension.order_column], "cate_with_groups")
        grouped = cate_with_groups.groupby([dimension.group_column, dimension.order_column], dropna=False, sort=False)
        for (group_label, group_order), subset in grouped:
            cate = subset["cate_hat"].dropna().astype(float)
            n_obs = int(len(cate))
            n_city = int(subset.loc[cate.index, "pku_city_code"].nunique())
            cate_std = float(cate.std(ddof=1)) if n_obs > 1 else 0.0
            cate_se = cate_std / sqrt(n_obs) if n_obs > 0 else np.nan
            cate_mean = float(cate.mean()) if n_obs > 0 else np.nan
            ci_padding = 1.96 * cate_se if n_obs > 1 else np.nan
            rows.append(
                {
                    "dimension_key": dimension.key,
                    "dimension_cn": dimension.label_cn,
                    "group_cn": str(group_label),
                    "group_order": int(group_order),
                    "n_obs": n_obs,
                    "n_city": n_city,
                    "cate_mean": cate_mean,
                    "cate_std": cate_std,
                    "cate_se": float(cate_se) if n_obs > 0 else np.nan,
                    "cate_mean_ci_lower_approx": cate_mean - ci_padding if n_obs > 1 else np.nan,
                    "cate_mean_ci_upper_approx": cate_mean + ci_padding if n_obs > 1 else np.nan,
                    "cate_q25": float(cate.quantile(0.25)) if n_obs > 0 else np.nan,
                    "cate_median": float(cate.quantile(0.50)) if n_obs > 0 else np.nan,
                    "cate_q75": float(cate.quantile(0.75)) if n_obs > 0 else np.nan,
                    "grouping_rule": dimension.rule,
                    "result_boundary": "基于当前 CATE 候选估计的分组摘要；近似区间仅描述组内 CATE 均值不确定性，不等同于严格 subgroup significance test。",
                }
            )
    result = pd.DataFrame(rows).sort_values(["dimension_key", "group_order", "group_cn"]).reset_index(drop=True)
    dimension_order = {dimension.key: idx for idx, dimension in enumerate(GROUP_DIMENSIONS)}
    result["dimension_order"] = result["dimension_key"].map(dimension_order)
    return result.sort_values(["dimension_order", "group_order", "group_cn"]).drop(columns="dimension_order").reset_index(drop=True)


def build_heterogeneity_group_summary(cate_frame: pd.DataFrame, model_frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cate_with_groups = attach_group_attributes(cate_frame, model_frame)
    summary = summarize_grouped_cate(cate_with_groups)
    return summary, cate_with_groups


def _normal_two_sided_p_value(z_stat: float) -> float:
    return float(erfc(abs(float(z_stat)) / sqrt(2.0)))


def _bootstrap_mean_differences(
    group_a_values: np.ndarray,
    group_b_values: np.ndarray,
    n_bootstrap: int,
    rng: np.random.Generator,
) -> np.ndarray:
    if n_bootstrap <= 0:
        raise ValueError("n_bootstrap must be positive")
    if len(group_a_values) == 0 or len(group_b_values) == 0:
        raise ValueError("Both groups must have at least one city-level CATE value")
    sample_a = rng.choice(group_a_values, size=(n_bootstrap, len(group_a_values)), replace=True)
    sample_b = rng.choice(group_b_values, size=(n_bootstrap, len(group_b_values)), replace=True)
    return sample_a.mean(axis=1) - sample_b.mean(axis=1)


def build_pairwise_group_differences(
    cate_with_groups: pd.DataFrame,
    n_bootstrap: int = 2000,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Build approximate pairwise CATE group-difference diagnostics.

    The input CATE table is city-year level. For difference diagnostics we first
    collapse to one CATE mean per city, then bootstrap cities within each group.
    This avoids giving cities with more observed years extra weight and keeps
    the output as an interpretable heterogeneity diagnostic rather than a
    replacement for the main DML ATE inference.
    """

    require_columns(cate_with_groups, ["pku_city_code", "cate_hat"], "cate_with_groups")
    rng = np.random.default_rng(random_seed)
    rows: list[dict[str, object]] = []
    for dimension in GROUP_DIMENSIONS:
        require_columns(cate_with_groups, [dimension.group_column, dimension.order_column], "cate_with_groups")
        city_level = (
            cate_with_groups.groupby(
                ["pku_city_code", dimension.group_column, dimension.order_column],
                as_index=False,
                dropna=False,
            )
            .agg(cate_city_mean=("cate_hat", "mean"))
            .sort_values([dimension.order_column, dimension.group_column, "pku_city_code"])
            .reset_index(drop=True)
        )
        groups = (
            city_level[[dimension.group_column, dimension.order_column]]
            .drop_duplicates()
            .sort_values([dimension.order_column, dimension.group_column])
            .itertuples(index=False, name=None)
        )
        for (group_a, order_a), (group_b, order_b) in combinations(list(groups), 2):
            values_a = city_level.loc[city_level[dimension.group_column] == group_a, "cate_city_mean"].to_numpy(float)
            values_b = city_level.loc[city_level[dimension.group_column] == group_b, "cate_city_mean"].to_numpy(float)
            mean_a = float(values_a.mean())
            mean_b = float(values_b.mean())
            difference = mean_a - mean_b
            boot = _bootstrap_mean_differences(values_a, values_b, n_bootstrap=n_bootstrap, rng=rng)
            bootstrap_se = float(boot.std(ddof=1)) if len(boot) > 1 else np.nan
            if np.isfinite(bootstrap_se) and bootstrap_se > 0:
                z_stat = difference / bootstrap_se
                p_value = _normal_two_sided_p_value(z_stat)
            else:
                z_stat = np.nan
                p_value = np.nan
            ci_lower, ci_upper = np.quantile(boot, [0.025, 0.975])
            if difference < 0:
                direction_cn = f"{group_a}组CATE更负"
            elif difference > 0:
                direction_cn = f"{group_b}组CATE更负"
            else:
                direction_cn = "两组CATE均值相同"
            rows.append(
                {
                    "dimension_key": dimension.key,
                    "dimension_cn": dimension.label_cn,
                    "group_a_cn": str(group_a),
                    "group_b_cn": str(group_b),
                    "group_a_order": int(order_a),
                    "group_b_order": int(order_b),
                    "n_city_a": int(len(values_a)),
                    "n_city_b": int(len(values_b)),
                    "cate_mean_a": mean_a,
                    "cate_mean_b": mean_b,
                    "mean_difference_a_minus_b": difference,
                    "bootstrap_se": bootstrap_se,
                    "ci_lower_bootstrap": float(ci_lower),
                    "ci_upper_bootstrap": float(ci_upper),
                    "z_stat_approx": float(z_stat) if np.isfinite(z_stat) else np.nan,
                    "p_value_approx": float(p_value) if np.isfinite(p_value) else np.nan,
                    "n_bootstrap": int(n_bootstrap),
                    "direction_cn": direction_cn,
                    "result_boundary": "城市层面CATE均值bootstrap组间差异诊断；用于异质性叙述，不等同于重新估计分组DML或严格因果效应差异检验。",
                }
            )
    result = pd.DataFrame(rows)
    dimension_order = {dimension.key: idx for idx, dimension in enumerate(GROUP_DIMENSIONS)}
    result["dimension_order"] = result["dimension_key"].map(dimension_order)
    return (
        result.sort_values(["dimension_order", "group_a_order", "group_b_order", "group_a_cn", "group_b_cn"])
        .drop(columns="dimension_order")
        .reset_index(drop=True)
    )
