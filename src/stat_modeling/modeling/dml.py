from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.base import BaseEstimator
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GroupKFold
from sklearn.model_selection import KFold


@dataclass(slots=True)
class DMLResult:
    ate: float
    std_error: float
    ci_lower: float
    ci_upper: float
    p_value: float
    nobs: int
    folds: int
    split_strategy: str
    covariance_type: str
    nuisance_model_y: str
    nuisance_model_t: str

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "ate": self.ate,
                    "std_error": self.std_error,
                    "ci_lower": self.ci_lower,
                    "ci_upper": self.ci_upper,
                    "p_value": self.p_value,
                    "nobs": self.nobs,
                    "folds": self.folds,
                    "split_strategy": self.split_strategy,
                    "covariance_type": self.covariance_type,
                    "nuisance_model_y": self.nuisance_model_y,
                    "nuisance_model_t": self.nuisance_model_t,
                }
            ]
        )


@dataclass(slots=True)
class DMLResiduals:
    y_res: np.ndarray
    t_res: np.ndarray
    model_frame: pd.DataFrame
    folds: int
    split_strategy: str
    nuisance_model_y: str
    nuisance_model_t: str


def residualize_partial_linear_dml(
    frame: pd.DataFrame,
    outcome_column: str,
    treatment_column: str,
    control_columns: list[str],
    folds: int = 5,
    random_seed: int = 42,
    group_column: str | None = None,
    cluster_column: str | None = None,
    model_y: BaseEstimator | None = None,
    model_t: BaseEstimator | None = None,
) -> DMLResiduals:
    if not control_columns:
        raise ValueError("control_columns cannot be empty for partial linear DML")

    required_columns = [outcome_column, treatment_column] + control_columns
    if group_column:
        required_columns.append(group_column)
    if cluster_column:
        required_columns.append(cluster_column)
    model_frame = frame.dropna(subset=required_columns).reset_index(drop=True)
    if len(model_frame) < folds:
        raise ValueError(f"Insufficient rows ({len(model_frame)}) for folds={folds}")

    y = model_frame[outcome_column].to_numpy(dtype=float)
    t = model_frame[treatment_column].to_numpy(dtype=float)
    x = model_frame[control_columns].to_numpy(dtype=float)
    groups = model_frame[group_column].to_numpy() if group_column else None

    model_y = model_y if model_y is not None else GradientBoostingRegressor(random_state=random_seed)
    model_t = model_t if model_t is not None else GradientBoostingRegressor(random_state=random_seed)
    if group_column:
        splitter = GroupKFold(n_splits=folds)
        splits = splitter.split(x, groups=groups)
        split_strategy = f"GroupKFold({group_column})"
    else:
        splitter = KFold(n_splits=folds, shuffle=True, random_state=random_seed)
        splits = splitter.split(x)
        split_strategy = "KFold"

    y_res = np.zeros(len(model_frame), dtype=float)
    t_res = np.zeros(len(model_frame), dtype=float)

    for train_idx, test_idx in splits:
        x_train, x_test = x[train_idx], x[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        t_train, t_test = t[train_idx], t[test_idx]

        fitted_y = clone(model_y).fit(x_train, y_train)
        fitted_t = clone(model_t).fit(x_train, t_train)

        y_res[test_idx] = y_test - fitted_y.predict(x_test)
        t_res[test_idx] = t_test - fitted_t.predict(x_test)

    return DMLResiduals(
        y_res=y_res,
        t_res=t_res,
        model_frame=model_frame,
        folds=folds,
        split_strategy=split_strategy,
        nuisance_model_y=type(model_y).__name__,
        nuisance_model_t=type(model_t).__name__,
    )


def fit_partial_linear_dml(
    frame: pd.DataFrame,
    outcome_column: str,
    treatment_column: str,
    control_columns: list[str],
    folds: int = 5,
    random_seed: int = 42,
    group_column: str | None = None,
    cluster_column: str | None = None,
    model_y: BaseEstimator | None = None,
    model_t: BaseEstimator | None = None,
) -> DMLResult:
    residuals = residualize_partial_linear_dml(
        frame=frame,
        outcome_column=outcome_column,
        treatment_column=treatment_column,
        control_columns=control_columns,
        folds=folds,
        random_seed=random_seed,
        group_column=group_column,
        cluster_column=cluster_column,
        model_y=model_y,
        model_t=model_t,
    )
    clusters = residuals.model_frame[cluster_column].to_numpy() if cluster_column else None

    if clusters is not None:
        ols = sm.OLS(residuals.y_res, sm.add_constant(residuals.t_res)).fit(
            cov_type="cluster",
            cov_kwds={"groups": clusters},
        )
        covariance_type = f"cluster({cluster_column})"
    else:
        ols = sm.OLS(residuals.y_res, sm.add_constant(residuals.t_res)).fit(cov_type="HC3")
        covariance_type = "HC3"
    ate = float(ols.params[1])
    std_error = float(ols.bse[1])
    ci_low, ci_high = ols.conf_int(alpha=0.05)[1]

    return DMLResult(
        ate=ate,
        std_error=std_error,
        ci_lower=float(ci_low),
        ci_upper=float(ci_high),
        p_value=float(ols.pvalues[1]),
        nobs=int(len(residuals.model_frame)),
        folds=residuals.folds,
        split_strategy=residuals.split_strategy,
        covariance_type=covariance_type,
        nuisance_model_y=residuals.nuisance_model_y,
        nuisance_model_t=residuals.nuisance_model_t,
    )
