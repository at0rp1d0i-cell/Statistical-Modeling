from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stat_modeling.modeling.dml import fit_partial_linear_dml


def test_fit_partial_linear_dml_recovers_positive_effect_on_synthetic_data():
    rng = np.random.default_rng(42)
    n = 800
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    treatment = 0.8 * x1 - 0.5 * x2 + rng.normal(scale=0.5, size=n)
    outcome = 1.5 * treatment + 0.7 * x1 + 0.2 * x2 + rng.normal(scale=0.5, size=n)
    frame = pd.DataFrame(
        {
            "outcome": outcome,
            "treatment": treatment,
            "x1": x1,
            "x2": x2,
        }
    )

    result = fit_partial_linear_dml(
        frame=frame,
        outcome_column="outcome",
        treatment_column="treatment",
        control_columns=["x1", "x2"],
        folds=5,
        random_seed=42,
    )

    assert 1.2 < result.ate < 1.8
    assert result.std_error > 0


def test_fit_partial_linear_dml_supports_grouped_cross_fitting_and_clustered_se():
    rng = np.random.default_rng(42)
    n_groups = 40
    group_size = 10
    group_ids = np.repeat(np.arange(n_groups), group_size)
    x1 = rng.normal(size=n_groups * group_size)
    x2 = rng.normal(size=n_groups * group_size)
    treatment = 0.5 * x1 + rng.normal(scale=0.3, size=n_groups * group_size)
    outcome = 1.0 * treatment + 0.2 * x2 + rng.normal(scale=0.3, size=n_groups * group_size)
    frame = pd.DataFrame(
        {
            "outcome": outcome,
            "treatment": treatment,
            "x1": x1,
            "x2": x2,
            "city_id": group_ids,
        }
    )

    result = fit_partial_linear_dml(
        frame=frame,
        outcome_column="outcome",
        treatment_column="treatment",
        control_columns=["x1", "x2"],
        folds=5,
        random_seed=42,
        group_column="city_id",
        cluster_column="city_id",
    )

    assert result.split_strategy == "GroupKFold(city_id)"
    assert result.covariance_type == "cluster(city_id)"
    assert result.std_error > 0


def test_fit_partial_linear_dml_accepts_custom_nuisance_models():
    rng = np.random.default_rng(42)
    n = 120
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    treatment = 0.4 * x1 + rng.normal(scale=0.2, size=n)
    outcome = -0.7 * treatment + 0.3 * x2 + rng.normal(scale=0.2, size=n)
    frame = pd.DataFrame(
        {
            "outcome": outcome,
            "treatment": treatment,
            "x1": x1,
            "x2": x2,
        }
    )
    nuisance = RandomForestRegressor(n_estimators=10, min_samples_leaf=3, random_state=42)

    result = fit_partial_linear_dml(
        frame=frame,
        outcome_column="outcome",
        treatment_column="treatment",
        control_columns=["x1", "x2"],
        folds=3,
        random_seed=42,
        model_y=nuisance,
        model_t=nuisance,
    )

    assert result.nuisance_model_y == "RandomForestRegressor"
    assert result.nuisance_model_t == "RandomForestRegressor"
    assert result.std_error > 0
