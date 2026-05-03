from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stat_modeling.policy_text.llm_schema import build_scoring_payload
from stat_modeling.policy_text.llm_schema import build_jsonl_batch
from stat_modeling.policy_text.llm_schema import validate_scoring_response


def test_build_scoring_payload_contains_three_scores_and_document_context():
    payload = build_scoring_payload(
        title="关于加快绿色低碳转型的意见",
        content_text="明确提出责任分工、量化指标和数字平台建设要求。",
    )

    assert payload["document"]["title"] == "关于加快绿色低碳转型的意见"
    assert "policy_strength" in payload["schema"]["properties"]
    assert "execution_clarity" in payload["schema"]["properties"]
    assert "digital_green_synergy" in payload["schema"]["properties"]
    assert "rubric" in payload["scoring_instructions"]


def test_validate_scoring_response_normalizes_three_scores():
    result = validate_scoring_response(
        {
            "policy_strength": 4,
            "execution_clarity": 3.5,
            "digital_green_synergy": 2,
        }
    )

    assert result["policy_strength"] == 4.0
    assert result["execution_clarity"] == 3.5


def test_build_jsonl_batch_includes_doc_id_and_payload():
    batch = build_jsonl_batch(
        [
            {
                "doc_id": "doc-1",
                "title": "政策文件",
                "source_url": "https://example.gov.cn/doc",
                "content_text": "推进数字化绿色转型。",
            }
        ]
    )

    assert '"doc_id": "doc-1"' in batch
    assert '"payload"' in batch
