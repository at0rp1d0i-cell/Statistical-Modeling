from __future__ import annotations

import numpy as np
import pandas as pd


LLM_SCORE_COLUMNS = ("llm_policy_strength", "llm_execution_clarity", "llm_digital_green_synergy")
RULE_SCORE_COLUMNS = ("policy_strength", "execution_clarity", "digital_green_synergy")
VALID_REVIEW_STATUSES = {"pending", "validated", "needs_review", "rejected"}


def summarize_score_alignment(frame: pd.DataFrame) -> dict[str, dict[bool, float]]:
    summary: dict[str, dict[bool, float]] = {}
    rule_columns = [column for column in frame.columns if column.startswith("has_")]
    score_columns = [column for column in ("policy_strength", "execution_clarity", "digital_green_synergy") if column in frame.columns]

    for rule_column in rule_columns:
        grouped = frame.groupby(rule_column)[score_columns].mean(numeric_only=True)
        for score_column in score_columns:
            summary[f"{score_column}_by_{rule_column.removeprefix('has_')}"] = grouped[score_column].to_dict()
    return summary


def build_llm_score_review_template(registry: pd.DataFrame) -> pd.DataFrame:
    required = ["doc_id", "title", "pub_date", "issuing_body", "admin_level", "source_url"]
    missing = [column for column in required if column not in registry.columns]
    if missing:
        raise ValueError(f"registry missing required columns: {missing}")

    columns = [*required]
    template = registry[columns].copy()
    for rule_column in RULE_SCORE_COLUMNS:
        if rule_column in registry.columns:
            template[f"rule_{rule_column}"] = registry[rule_column]
    for score_column in LLM_SCORE_COLUMNS:
        template[score_column] = pd.NA
    template["llm_model"] = pd.NA
    template["llm_run_id"] = pd.NA
    template["repeat_run_id"] = 1
    template["human_review_status"] = "pending"
    template["reviewer_notes"] = pd.NA
    return template.sort_values(["pub_date", "doc_id"]).reset_index(drop=True)


def validate_llm_score_records(frame: pd.DataFrame) -> pd.DataFrame:
    required = ["doc_id", *LLM_SCORE_COLUMNS, "human_review_status"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"score frame missing required columns: {missing}")

    result = frame[["doc_id", "human_review_status", *LLM_SCORE_COLUMNS]].copy()
    for score_column in LLM_SCORE_COLUMNS:
        result[score_column] = pd.to_numeric(result[score_column], errors="coerce")
    result["score_complete"] = result[list(LLM_SCORE_COLUMNS)].notna().all(axis=1)
    result["score_range_valid"] = result[list(LLM_SCORE_COLUMNS)].apply(lambda row: row.dropna().between(1, 5).all(), axis=1)
    result["human_review_status_valid"] = result["human_review_status"].isin(VALID_REVIEW_STATUSES)
    result["human_validated"] = result["human_review_status"].eq("validated")
    result["validation_ready"] = (
        result["score_complete"]
        & result["score_range_valid"]
        & result["human_review_status_valid"]
        & result["human_validated"]
    )
    return result


def build_llm_validation_readiness_table(score_frame: pd.DataFrame, registry: pd.DataFrame | None = None) -> pd.DataFrame:
    validated = validate_llm_score_records(score_frame)
    total_registered = int(registry["doc_id"].nunique()) if registry is not None and "doc_id" in registry.columns else int(score_frame["doc_id"].nunique())
    duplicate_doc_rows = int(score_frame.duplicated(subset=["doc_id"], keep=False).sum())
    completed_rows = int(validated["score_complete"].sum())
    range_valid_rows = int((validated["score_complete"] & validated["score_range_valid"]).sum())
    human_validated_rows = int(validated["human_validated"].sum())
    ready_rows = int(validated["validation_ready"].sum())
    missing_registered_docs = max(total_registered - int(score_frame["doc_id"].nunique()), 0)
    readiness_status = "ready" if total_registered > 0 and ready_rows == total_registered and duplicate_doc_rows == 0 else "not_ready"

    mean_abs_rule_llm_delta = np.nan
    if set(LLM_SCORE_COLUMNS).issubset(score_frame.columns) and {"rule_policy_strength", "rule_execution_clarity", "rule_digital_green_synergy"}.issubset(score_frame.columns):
        deltas = []
        for llm_column, rule_column in zip(
            LLM_SCORE_COLUMNS,
            ("rule_policy_strength", "rule_execution_clarity", "rule_digital_green_synergy"),
            strict=True,
        ):
            llm_values = pd.to_numeric(score_frame[llm_column], errors="coerce")
            rule_values = pd.to_numeric(score_frame[rule_column], errors="coerce")
            delta = (llm_values - rule_values).abs().dropna()
            if not delta.empty:
                deltas.extend(delta.tolist())
        if deltas:
            mean_abs_rule_llm_delta = float(np.mean(deltas))

    status_note = (
        "LLM评分与人工复核均完成，可进入机制候选建模。"
        if readiness_status == "ready"
        else "LLM评分或人工复核尚未完成；当前只能作为评分准备/校验框架，不能作为正式机制证据。"
    )
    return pd.DataFrame(
        [
            {
                "validation_scope": "policy_llm_scoring",
                "total_registered_docs": total_registered,
                "score_rows": int(len(score_frame)),
                "completed_score_rows": completed_rows,
                "range_valid_score_rows": range_valid_rows,
                "human_validated_rows": human_validated_rows,
                "validation_ready_rows": ready_rows,
                "missing_registered_docs": missing_registered_docs,
                "duplicate_doc_rows": duplicate_doc_rows,
                "mean_abs_rule_llm_delta": mean_abs_rule_llm_delta,
                "readiness_status": readiness_status,
                "status_note": status_note,
            }
        ]
    )
