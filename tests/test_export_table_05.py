from pathlib import Path
from subprocess import run


def test_export_table_05_runs():
    repo = Path(__file__).resolve().parents[1]
    source = repo / "outputs" / "tables" / "table_05_policy_seed_mechanism_candidate.csv"
    if not source.exists():
        source.write_text(
            (
                "variable_name,coefficient,std_error,ci_lower,ci_upper,p_value,nobs\n"
                "sum_policy_strength_city_year,1.0,0.1,0.8,1.2,0.01,100\n"
            ),
            encoding="utf-8",
        )
    result = run(
        ["python3", "src/24_export_table_05.py"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert (repo / "outputs" / "tables" / "table_05_policy_seed_mechanism_candidate.tex").exists()
