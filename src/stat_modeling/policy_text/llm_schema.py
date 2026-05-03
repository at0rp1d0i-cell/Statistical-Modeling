from __future__ import annotations

import json
from typing import Iterable


SCORE_FIELDS = ("policy_strength", "execution_clarity", "digital_green_synergy")

SCORE_RUBRIC = {
    "policy_strength": "政策约束力度、任务密度、量化目标和推进强度，1=弱，5=强。",
    "execution_clarity": "责任分工、时间节点、考核监督和执行安排清晰度，1=模糊，5=清晰。",
    "digital_green_synergy": "数字化、数据、平台、智能技术服务绿色低碳转型的协同程度，1=无体现，5=高度明确。",
}


def build_scoring_payload(
    title: str,
    content_text: str,
    doc_id: str | None = None,
    source_url: str | None = None,
) -> dict[str, object]:
    return {
        "document": {
            "doc_id": doc_id,
            "title": title,
            "source_url": source_url,
            "content_text": content_text,
            "task_role": "mechanism_or_moderation_only",
        },
        "scoring_instructions": {
            "language": "Chinese",
            "scale": "1-5 integer or half-point decimal scores are allowed.",
            "boundary": "Scores are mechanism/moderation variables only; do not infer the main causal effect.",
            "rubric": SCORE_RUBRIC,
        },
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "policy_strength": {"type": "number", "minimum": 1, "maximum": 5},
                "execution_clarity": {"type": "number", "minimum": 1, "maximum": 5},
                "digital_green_synergy": {"type": "number", "minimum": 1, "maximum": 5},
            },
            "required": ["policy_strength", "execution_clarity", "digital_green_synergy"],
        },
    }


def validate_scoring_response(response: dict[str, object]) -> dict[str, float]:
    missing = [field for field in SCORE_FIELDS if field not in response]
    if missing:
        raise ValueError(f"LLM scoring response missing fields: {missing}")
    extra = sorted(set(response) - set(SCORE_FIELDS))
    if extra:
        raise ValueError(f"LLM scoring response contains unsupported fields: {extra}")

    normalized: dict[str, float] = {}
    for field in SCORE_FIELDS:
        value = float(response[field])
        if value < 1 or value > 5:
            raise ValueError(f"{field} must be within [1, 5], got {value}")
        normalized[field] = value
    return normalized


def build_jsonl_batch(records: Iterable[dict[str, object]]) -> str:
    lines: list[str] = []
    for record in records:
        payload = build_scoring_payload(
            doc_id=str(record.get("doc_id") or ""),
            title=str(record["title"]),
            source_url=str(record.get("source_url") or ""),
            content_text=str(record["content_text"]),
        )
        lines.append(json.dumps({"doc_id": payload["document"]["doc_id"], "payload": payload}, ensure_ascii=False))
    return "\n".join(lines) + ("\n" if lines else "")
