from pathlib import Path
from subprocess import run


def test_mechanism_seed_regression_script_runs():
    result = run(
        ["python3", "src/23_mechanism_seed_regression.py"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
