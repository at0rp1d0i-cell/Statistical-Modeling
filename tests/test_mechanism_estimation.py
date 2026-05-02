from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stat_modeling.modeling.mechanism import fit_candidate_mechanism_ols


def test_fit_candidate_mechanism_ols_returns_result_rows():
    rng = np.random.default_rng(42)
    n = 100
    frame = pd.DataFrame(
        {
            "y": rng.normal(size=n),
            "t": rng.normal(size=n),
            "m1": rng.normal(size=n),
            "m2": rng.normal(size=n),
            "x1": rng.normal(size=n),
            "city": np.repeat(range(20), 5),
        }
    )
    result = fit_candidate_mechanism_ols(
        frame=frame,
        outcome_column="y",
        treatment_column="t",
        mechanism_columns=["m1", "m2"],
        control_columns=["x1"],
        cluster_column="city",
    )
    assert len(result) == 2
    assert set(result["variable_name"]) == {"m1", "m2"}
