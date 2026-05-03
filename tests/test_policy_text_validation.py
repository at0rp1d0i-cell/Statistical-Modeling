from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stat_modeling.policy_text.validation import summarize_score_alignment
from stat_modeling.policy_text.validation import build_llm_score_review_template
from stat_modeling.policy_text.validation import build_llm_validation_readiness_table
from stat_modeling.policy_text.validation import validate_llm_score_records


def test_summarize_score_alignment_reports_rule_llm_directions():
    frame = pd.DataFrame(
        [
            {"has_quant_target": True, "policy_strength": 4.5},
            {"has_quant_target": False, "policy_strength": 1.0},
        ]
    )

    summary = summarize_score_alignment(frame)

    assert "policy_strength_by_quant_target" in summary
    assert summary["policy_strength_by_quant_target"][True] > summary["policy_strength_by_quant_target"][False]


def test_build_llm_score_review_template_keeps_rule_scores_blank_llm_scores():
    registry = pd.DataFrame(
        [
            {
                "doc_id": "doc-1",
                "title": "政策文件",
                "pub_date": "2021-01-01",
                "issuing_body": "国务院",
                "admin_level": "central",
                "source_url": "https://example.gov.cn/doc",
                "policy_strength": 4.0,
                "execution_clarity": 3.0,
                "digital_green_synergy": 2.0,
            }
        ]
    )

    template = build_llm_score_review_template(registry)

    assert template.loc[0, "rule_policy_strength"] == 4.0
    assert pd.isna(template.loc[0, "llm_policy_strength"])
    assert template.loc[0, "human_review_status"] == "pending"


def test_validate_llm_score_records_requires_scores_and_human_validation():
    frame = pd.DataFrame(
        [
            {
                "doc_id": "doc-1",
                "llm_policy_strength": 4.0,
                "llm_execution_clarity": 3.0,
                "llm_digital_green_synergy": 2.0,
                "human_review_status": "validated",
            },
            {
                "doc_id": "doc-2",
                "llm_policy_strength": None,
                "llm_execution_clarity": None,
                "llm_digital_green_synergy": None,
                "human_review_status": "pending",
            },
        ]
    )

    detail = validate_llm_score_records(frame)

    assert detail.loc[0, "validation_ready"]
    assert not detail.loc[1, "validation_ready"]


def test_build_llm_validation_readiness_table_reports_not_ready_for_template():
    registry = pd.DataFrame(
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
    )
    template = build_llm_score_review_template(registry)

    table = build_llm_validation_readiness_table(template, registry)

    assert table.loc[0, "readiness_status"] == "not_ready"
    assert table.loc[0, "completed_score_rows"] == 0
