from pathlib import Path
from subprocess import run

import pandas as pd


def test_prepare_policy_llm_scoring_batch_runs_with_explicit_paths(tmp_path):
    registry_path = tmp_path / "registry.csv"
    batch_jsonl = tmp_path / "batch.jsonl"
    review_template = tmp_path / "review.csv"
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
                "content_text": "提出量化目标、责任分工和数字平台建设。",
                "policy_strength": 4.0,
                "execution_clarity": 3.0,
                "digital_green_synergy": 2.0,
            }
        ]
    ).to_csv(registry_path, index=False)

    result = run(
        [
            "python3",
            "src/30_prepare_policy_llm_scoring_batch.py",
            "--registry-path",
            str(registry_path),
            "--batch-jsonl-path",
            str(batch_jsonl),
            "--review-template-path",
            str(review_template),
            "--summary-path",
            str(summary),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert batch_jsonl.exists()
    assert review_template.exists()
    assert summary.exists()
    assert '"doc_id": "doc-1"' in batch_jsonl.read_text(encoding="utf-8")
    exported = pd.read_csv(review_template)
    assert "llm_policy_strength" in exported.columns
    assert exported.loc[0, "human_review_status"] == "pending"
