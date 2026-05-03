# Policy LLM Validation Readiness Implementation Plan

<execution_handoff>
  <executor>codex</executor>
  <primary_mode>ralph</primary_mode>
  <rule>推进整体政策文本机制模块，但不得虚构 LLM 分数或将 seed 结果写成最终机制证据。</rule>
</execution_handoff>

**Goal:** 将政策文本模块从 `seed_rule_proxy` 技术链路推进到可执行的 validated LLM scoring 准备状态：生成 LLM scoring payload、人工/LLM 复核模板、验证明细和 readiness 表。

**Architecture:** 保持外部 LLM 调用与本仓库可复现分析解耦。本轮只生成批处理 JSONL 与复核模板，并在没有真实 LLM 分数时明确输出 `not_ready`。后续用户或代理填入真实 LLM 分数和人工复核状态后，再运行同一验证脚本更新 readiness。

**Tech Stack:** Python standard library, pandas, existing `stat_modeling.policy_text` package, pytest, Markdown docs.

---

### Task 1: 增强 LLM schema 与验证工具

**Files:**
- Modify: `src/stat_modeling/policy_text/llm_schema.py`
- Modify: `src/stat_modeling/policy_text/validation.py`
- Modify: `tests/test_policy_text_llm_schema.py`
- Modify: `tests/test_policy_text_validation.py`

**Steps:**
1. 为三个 LLM 核心指标补充 rubric。
2. 添加 LLM JSONL batch 生成工具。
3. 添加 LLM score review template、逐行验证和 readiness 汇总函数。

### Task 2: 添加 CLI 脚本

**Files:**
- Create: `src/30_prepare_policy_llm_scoring_batch.py`
- Create: `src/31_validate_policy_llm_scores.py`
- Create: `tests/test_policy_llm_scoring_batch_smoke.py`
- Create: `tests/test_policy_llm_validation_readiness_smoke.py`

**Steps:**
1. 从 seed scored registry 生成 JSONL payload。
2. 生成含规则分数和空白 LLM 分数字段的复核模板。
3. 生成 validation detail 与 Table 13 readiness。
4. 在无真实 LLM 分数时输出 `not_ready`，防止误写为正式机制证据。

### Task 3: 同步论文与证据链

**Files:**
- Modify: `src/26_export_evidence_synthesis.py`
- Modify: `tests/test_export_evidence_synthesis.py`
- Modify: `README.md`
- Modify: `docs/paper/01_draft.md`
- Modify: `docs/paper/02_manuscript_v0_1.md`
- Modify: `docs/paper/decision-log.md`
- Modify: `docs/paper/table-figure-inventory.md`

**Steps:**
1. Table 9 政策文本机制行读取 Table 13 readiness。
2. 文稿明确 Table 13 为验证就绪度，不是机制结果。
3. 表图清单新增 Table 13。

### Task 4: 验证、提交、推送

**Commands:**
- `python3 src/30_prepare_policy_llm_scoring_batch.py`
- `python3 src/31_validate_policy_llm_scores.py`
- `python3 src/26_export_evidence_synthesis.py`
- `python3 -m pytest -q`
- `python3 -m py_compile $(find src tests -name '*.py' | sort)`
- `git diff --check`
- Lore protocol commit and push.
