from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import statsmodels.api as sm


@dataclass(slots=True)
class MechanismResult:
    variable_name: str
    coefficient: float
    std_error: float
    ci_lower: float
    ci_upper: float
    p_value: float
    nobs: int

    def to_record(self) -> dict[str, object]:
        return {
            "variable_name": self.variable_name,
            "coefficient": self.coefficient,
            "std_error": self.std_error,
            "ci_lower": self.ci_lower,
            "ci_upper": self.ci_upper,
            "p_value": self.p_value,
            "nobs": self.nobs,
        }


def fit_candidate_mechanism_ols(
    frame: pd.DataFrame,
    outcome_column: str,
    treatment_column: str,
    mechanism_columns: list[str],
    control_columns: list[str],
    cluster_column: str,
) -> pd.DataFrame:
    results: list[dict[str, object]] = []
    for mechanism in mechanism_columns:
        required = [outcome_column, treatment_column, mechanism, cluster_column] + control_columns
        filtered = frame.dropna(subset=required).copy()
        design = filtered[[treatment_column, mechanism] + control_columns]
        design = sm.add_constant(design)
        model = sm.OLS(filtered[outcome_column], design).fit(
            cov_type="cluster",
            cov_kwds={"groups": filtered[cluster_column]},
        )
        ci_low, ci_high = model.conf_int().loc[mechanism]
        results.append(
            MechanismResult(
                variable_name=mechanism,
                coefficient=float(model.params[mechanism]),
                std_error=float(model.bse[mechanism]),
                ci_lower=float(ci_low),
                ci_upper=float(ci_high),
                p_value=float(model.pvalues[mechanism]),
                nobs=int(len(filtered)),
            ).to_record()
        )
    return pd.DataFrame(results)
