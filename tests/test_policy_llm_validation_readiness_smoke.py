from pathlib import Path
from subprocess import run

import pandas as pd


def test_validate_policy_llm_scores_runs_with_explicit_paths(tmp_path):
    registry_path = tmp_path / "registry.csv"
    score_path = tmp_path / "scores.csv"
    detail_path = tmp_path / "detail.csv"
    output_csv = tmp_path / "table_13.csv"
    output_tex = tmp_path / "table_13.tex"
    summary = tmp_path / "summary.txt"
    pd.DataFrame(
        [
            {
                "doc_id": "doc-1",
                "title": "政策文件",
                "pub_date": "2021-01-01",
                "issuing_body": "国务院",
                "admin_level": "central",
                "source_url": "https://example.gov.cn/doc",
            }
        ]
    ).to_csv(registry_path, index=False)
    pd.DataFrame(
        [
            {
                "doc_id": "doc-1",
                "llm_policy_strength": 4.0,
                "llm_execution_clarity": 3.0,
                "llm_digital_green_synergy": 2.0,
                "human_review_status": "validated",
            }
        ]
    ).to_csv(score_path, index=False)

    result = run(
        [
            "python3",
            "src/31_validate_policy_llm_scores.py",
            "--registry-path",
            str(registry_path),
            "--score-path",
            str(score_path),
            "--detail-output-path",
            str(detail_path),
            "--output-csv-path",
            str(output_csv),
            "--output-tex-path",
            str(output_tex),
            "--summary-path",
            str(summary),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert detail_path.exists()
    assert output_csv.exists()
    assert output_tex.exists()
    table = pd.read_csv(output_csv)
    assert table.loc[0, "readiness_status"] == "ready"
    assert table.loc[0, "validation_ready_rows"] == 1
